import io
import csv
import os.path
import logging
import mimetypes
from itertools import chain
from datetime import datetime

from dateutil.tz import tzutc
from django.db import transaction
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from rolepermissions.roles import get_user_roles
from rolepermissions.checkers import has_role

import peer_review.etl as etl
from peer_review.api.util import merge_validations, validate_rubric, raise_if_not_current_user, \
    raise_if_peer_review_not_given_to_student
from peer_review.util import to_camel_case, keymap_all
from peer_review.exceptions import ReviewsInProgressException, APIException
from peer_review.decorators import authorized_endpoint, authorized_json_endpoint, \
    authenticated_json_endpoint, json_body
from peer_review.models import CanvasCourse, CanvasStudent, CanvasAssignment, CanvasSubmission, \
    Rubric, Criterion, PeerReview, PeerReviewComment, PeerReviewEvaluation, PeerReviewDistribution
from peer_review.queries import InstructorDashboardStatus, StudentDashboardStatus, ReviewStatus, \
    RubricForm, Comments, Evaluations, Reviews


LOGGER = logging.getLogger(__name__)


@authenticated_json_endpoint
def logged_in_user_details(request):
    roles = [role.get_name() for role in get_user_roles(request.user)]
    course_id = request.session['lti_launch_params']['custom_canvas_course_id']
    course_name = request.session['lti_launch_params']['context_title']
    user_id = request.session['lti_launch_params']['custom_canvas_user_id']
    return {
        'username': request.user.username,
        'user_id': int(user_id),
        'course_id': int(course_id),
        'course_name': course_name,
        'roles': roles
    }


# TODO refactor this based on what we're actually using on the new students list implementation
@authorized_json_endpoint(roles=['instructor'])
def all_students(request, course_id):
    etl.persist_sections(course_id)
    etl.persist_students(course_id)

    course_model = CanvasCourse.objects.get(id=course_id)
    course = {'id': course_model.id, 'name': course_model.name}

    students = []
    for student in course_model.students.all():
        sections = []
        for section in student.sections.filter(course_id=course_id):
            sections.append({
                'id': section.id,
                'name': section.name,
                'course': course
            })
        students.append({
            'id': student.id,
            'sortable_name': student.sortable_name,
            'full_name': student.full_name,
            'username': student.username,
            'sections': sections,
            'course': course
        })

    return students


@authorized_json_endpoint(roles=['instructor'])
def all_peer_review_assignment_details(request, course_id):
    etl.persist_course(course_id)
    assignments = etl.persist_assignments(course_id)
    fetched_assignment_ids = tuple(map(lambda a: a.id, assignments))

    details = InstructorDashboardStatus.get(course_id, fetched_assignment_ids)

    validations = {a.id: a.validation for a in assignments}
    details_with_validations = merge_validations(details, validations)

    return keymap_all(to_camel_case, details_with_validations)


@authorized_json_endpoint(roles=['student'])
def assigned_work(request, course_id, student_id):
    raise_if_not_current_user(request, student_id)
    return StudentDashboardStatus.assigned_work(course_id, student_id)


@authorized_json_endpoint(roles=['student'])
def completed_work(request, course_id, student_id):
    raise_if_not_current_user(request, student_id)
    return StudentDashboardStatus.completed_work(course_id, student_id)


# TODO move this to the queries namespace
def _denormalize_reviews_given(reviews):

    peer_review_ids = sorted(r.id for r in reviews)
    student_numbers = {pr_id: i for i, pr_id in enumerate(peer_review_ids)}

    return {
        'title': reviews[0].submission.assignment.title,
        'entries': [
            {
                'id': review.id,
                'student_id': student_numbers[review.id],
                'entries': [{'id': comment.id,
                             'heading': comment.criterion.description,
                             'content': comment.comment}
                            for comment in review.comments.all().order_by('criterion_id')]
            }
            for review in reviews
            if review.comments.exists()
        ]
    }


@authorized_json_endpoint(roles=['student'])
def reviews_given(request, course_id, student_id, rubric_id):
    raise_if_not_current_user(request, student_id)

    reviews = PeerReview.objects.filter(
        student_id=student_id,
        submission__assignment__course_id=course_id,
        submission__assignment__rubric_for_prompt=rubric_id
    )\
        .prefetch_related('comments')\
        .order_by('id')

    return _denormalize_reviews_given(reviews)


@authorized_json_endpoint(roles=['student'])
def reviews_received(request, course_id, student_id, rubric_id):
    raise_if_not_current_user(request, student_id)
    return Reviews.reviews_received(course_id, student_id, rubric_id=rubric_id)


@authorized_json_endpoint(roles=['student'])
def mandatory_peer_review_evaluations(request, course_id, student_id):
    return Evaluations.pending_mandatory_evaluations(course_id, student_id)


@require_POST
@json_body
@authorized_json_endpoint(roles=['student'])
def submit_peer_review_evaluation(request, body, course_id, student_id, peer_review_id):
    raise_if_not_current_user(request, student_id)
    raise_if_peer_review_not_given_to_student(request, student_id, peer_review_id)

    PeerReviewEvaluation.objects.create(
        peer_review_id=peer_review_id,
        usefulness=body['usefulness'],
        comment=body['comment']
    )

    return True


@authorized_json_endpoint(roles=['instructor'])
def review_status(request, course_id, rubric_id):
    return ReviewStatus.status_for_rubric(course_id, rubric_id)


@authorized_json_endpoint(roles=['instructor'])
def rubric_info_for_peer_review_assignment(request, course_id, passback_assignment_id):
    try:
        passback_assignment = CanvasAssignment.objects.get(id=passback_assignment_id)
    except CanvasAssignment.DoesNotExist:
        raise Http404

    # TODO might need to persist course here if assignment-level launches are added for instructors
    course = CanvasCourse.objects.get(id=course_id)
    fetched_assignments = etl.persist_assignments(course_id)

    return RubricForm.rubric_info(course, passback_assignment, fetched_assignments)


@require_POST
@json_body
@authorized_json_endpoint(roles=['instructor'], default_status_code=201)
def create_or_update_rubric(request, params, course_id):
    try:
        with transaction.atomic():
            # my kingdom for destructuring assignment in Python :/
            objects = validate_rubric(int(course_id), params)
            prompt_assignment = objects['prompt_assignment']
            passback_assignment = objects['peer_review_assignment']
            revision_assignment = objects['revision_assignment']
            rubric_description = objects['rubric_description']
            criteria = objects['criteria']
            peer_review_open_date = objects['peer_review_open_date']
            pr_open_date_is_prompt_due_date = objects['peer_review_open_date_is_prompt_due_date']

            rubric, created = Rubric.objects.update_or_create(
                reviewed_assignment=prompt_assignment,
                defaults={
                    'description': rubric_description,
                    'reviewed_assignment': prompt_assignment,
                    'passback_assignment': passback_assignment,
                    'revision_assignment': revision_assignment,
                    'peer_review_open_date': peer_review_open_date,
                    'peer_review_open_date_is_prompt_due_date': pr_open_date_is_prompt_due_date,
                    'distribute_peer_reviews_for_sections': False
                }
            )

            if not created:
                try:
                    distribution = PeerReviewDistribution.objects.get(rubric_id=rubric.id)
                    if distribution.is_distribution_complete:
                        raise ReviewsInProgressException
                except PeerReviewDistribution.DoesNotExist:
                    pass
                Criterion.objects.filter(rubric_id=rubric.id).delete()

            rubric.save()
            for criterion in criteria:
                criterion.rubric_id = rubric.id
                criterion.save()

        return params
    except ReviewsInProgressException:
        error = 'Rubric is read-only because reviews are in progress.'
        raise APIException(data={'error': error}, status_code=403)


@authorized_endpoint(roles=['instructor', 'student'])
def submission_for_review(request, course_id, review_id):
    try:
        peer_review = PeerReview.objects.get(id=review_id)
    except PeerReview.DoesNotExist:
        raise Http404

    logged_in_user_id = int(request.session['lti_launch_params']['custom_canvas_user_id'])
    if has_role(request.user, 'student') and logged_in_user_id != peer_review.student_id:
        msg = 'User %s tried to download submission for a peer review (ID %s) they were not assigned'
        LOGGER.warning(msg, logged_in_user_id, review_id)
        raise PermissionDenied

    submission = peer_review.submission
    submission_path = os.path.join(settings.MEDIA_ROOT, 'submissions', submission.filename)

    with open(submission_path, 'rb') as submission_file:
        submission_bytes = submission_file.read()

    content_type = mimetypes.guess_type(submission.filename)[0] or 'application/octet-stream'
    response = HttpResponse(submission_bytes, content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % submission.filename

    return response


@authorized_json_endpoint(roles=['student'])
def rubric_for_review(request, course_id, review_id):
    try:
        peer_review = PeerReview.objects.get(id=review_id)
    except PeerReview.DoesNotExist:
        raise Http404

    logged_in_user_id = int(request.session['lti_launch_params']['custom_canvas_user_id'])
    if logged_in_user_id != peer_review.student_id:
        msg = 'User %s tried to access rubric for a review (ID %s) they were not assigned'
        LOGGER.warning(msg, logged_in_user_id, review_id)
        raise PermissionDenied

    rubric = peer_review.submission.assignment.rubric_for_prompt

    return {
        'description': rubric.description,
        'criteria': [{'id': c.id, 'description': c.description} for c in rubric.criteria.all()]
    }


@require_POST
@json_body
@authorized_json_endpoint(roles=['student'], default_status_code=201)
def submit_peer_review(request, params, course_id, review_id):

    logged_in_user_id = int(request.session['lti_launch_params']['custom_canvas_user_id'])

    try:
        peer_review = PeerReview.objects.get(id=review_id)
    except PeerReview.DoesNotExist:
        raise Http404

    if logged_in_user_id != peer_review.student_id:
        msg = 'User %s tried to submit comments for a review (ID %s) that they were not assigned'
        LOGGER.warning(msg, logged_in_user_id, review_id)
        error = 'You were not assigned that peer review.'
        raise APIException(data={'error': error}, status_code=403)

    student = CanvasStudent.objects.get(id=logged_in_user_id)
    comments = params['comments']
    rubric = peer_review.submission.assignment.rubric_for_prompt

    criteria_ids = set(rubric.criteria.all().values_list('id', flat=True))
    user_criteria_ids = set(int(c['criterion_id']) for c in comments)
    if criteria_ids != user_criteria_ids:
        msg = 'Criterion IDs do not match for review %s submitted by student "%s"'
        LOGGER.warning(msg, review_id, student.username)
        raise APIException(data={'error': 'Criterion IDs do not match.'}, status_code=400)

    existing_comments = PeerReviewComment.objects.filter(peer_review=peer_review)
    if existing_comments.exists():
        LOGGER.warning(
            'Student %s tried to submit a review that has already been completed',
            student.username
        )
        if existing_comments.count() != rubric.criteria.count():
            LOGGER.warning(
                'Student %s has %d out of %d comments for review %s',
                student.username,
                existing_comments.count(),
                rubric.criteria.count(),
                review_id
            )
        msg = 'Review %s has already been completed previously.' % review_id
        raise APIException(data={'error': msg}, status_code=400)

    comments = [
        PeerReviewComment(
            criterion_id=c['criterion_id'],
            comment=c['comment'],
            commented_at_utc=datetime.now(tzutc()),
            peer_review=peer_review
        )
        for c in comments
    ]

    with transaction.atomic():
        existing_comments.delete()
        for comment in comments:
            comment.save()

    return params


@authorized_endpoint(roles=['instructor'])
def csv_for_student_and_rubric(request, course_id, student_id, rubric_id=None):

    try:
        all_comments = Comments.all_comments_for_student(
            student_id=student_id,
            rubric_id=rubric_id
        )
    except Rubric.DoesNotExist:
        LOGGER.error('Rubric %s does not exist to download CSV data', rubric_id)
        raise Http404
    except CanvasStudent.DoesNotExist:
        LOGGER.error('Student %s does not exist to download CSV data', student_id)
        raise Http404

    rows = [['Prompt', 'Reviewer', 'Author', 'Criterion ID', 'Comment']] + [
        [
            comment.peer_review.submission.assignment.title,
            comment.peer_review.student.sortable_name,
            comment.peer_review.submission.author.sortable_name,
            comment.criterion.id,
            comment.comment
        ]
        for comment in all_comments
    ]

    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for row in rows:
        writer.writerow(row)
    csv_data = output.getvalue()

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = "attachment"

    return response


@authorized_json_endpoint(roles=['instructor'])
def student_info(request, course_id, student_id):
    try:
        student = CanvasStudent.objects.get(id=student_id)
    except CanvasStudent.DoesNotExist:
        raise Http404

    if not student.courses.filter(id=course_id).exists():
        msg = 'Student %s is not a part of course %s' % (student_id, course_id)
        raise APIException(data={'error': msg}, status_code=403)

    return {
        'id': student.id,
        'full_name': student.full_name,
        'sortable_name': student.sortable_name
    }


@authorized_json_endpoint(roles=['instructor'])
def all_rubrics_for_course(request, course_id):
    rubrics = Rubric.objects.filter(reviewed_assignment__course__id=course_id)
    return [
        {
            'id': r.id,
            'prompt_id': r.reviewed_assignment.id,
            'prompt_title': r.reviewed_assignment.title
        }
        for r in rubrics
    ]


@authorized_json_endpoint(roles=['instructor'])
def all_rubric_statuses_for_student(request, course_id, student_id):
    try:
        student = CanvasStudent.objects.get(id=student_id)
    except CanvasStudent.DoesNotExist:
        raise Http404

    return ReviewStatus.all_rubric_statuses_for_student(course_id, student)


@authorized_json_endpoint(roles=['instructor'])
def rubric_status_for_student(request, course_id, rubric_id, student_id):
    try:
        rubric = Rubric.objects.get(id=rubric_id)
    except Rubric.DoesNotExist:
        msg = 'The specified rubric does not exist.'
        raise APIException(data={'error': msg}, status_code=404)

    try:
        student = CanvasStudent.objects.get(id=student_id)
    except CanvasStudent.DoesNotExist:
        msg = 'The specified student does not exist.'
        raise APIException(data={'error': msg}, status_code=404)

    return ReviewStatus.detailed_rubric_status_for_student(course_id, student, rubric)


@authorized_json_endpoint(roles=['instructor'])
def single_review(request, course_id, review_id):
    try:
        return Reviews.single_review(course_id, review_id)
    except PeerReview.DoesNotExist:
        raise Http404


# Django doesn't let you declare the HTTP method as part of the URL conf, so...
# TODO could probably refactor this into something generic
def dispatch_peer_review_request(*args, **kwargs):
    request = args[0]
    if request.method == 'POST':
        view = submit_peer_review
    elif request.method == 'GET':
        view = single_review
    else:
        msg = 'Unsupported method %s' % request.method
        return JsonResponse({'error': msg}, status=405)
    return view(*args, **kwargs)
