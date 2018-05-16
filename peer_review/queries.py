import json
from itertools import chain
from toolz.dicttoolz import valfilter
from toolz.functoolz import thread_last
from toolz.itertoolz import groupby, unique
from django.db import connection
from django.db.models import BooleanField, Subquery, OuterRef, Count, Case, When, Value, F, Q

from peer_review.util import some, fetchall_dicts
from peer_review.models import PeerReview, Criterion, PeerReviewComment, CanvasCourse, Rubric, \
    CanvasAssignment, PeerReviewDistribution

# TODO move to settings
API_DATE_FORMAT = '%Y-%m-%d %H:%M:%SZ'


class InstructorDashboardStatus:
    query = """
    SELECT
      total_reviews.rubric_id,
      total_reviews.prompt_id,
      peer_review_assignments.id           AS peer_review_assignment_id,
      peer_review_assignments.title        AS peer_review_title,
      CASE WHEN peer_review_distributions.distributed_at_utc IS NOT NULL
        THEN peer_review_distributions.distributed_at_utc
      ELSE open_date
      END                                  AS open_date,
      peer_review_assignments.due_date_utc AS due_date,
      number_of_completed_reviews,
      number_of_assigned_reviews,
      CASE WHEN peer_review_distributions.is_distribution_complete IS TRUE
        THEN TRUE
      ELSE FALSE
      END                                  AS reviews_in_progress
    FROM
      canvas_assignments peer_review_assignments
      LEFT JOIN
      (SELECT
         rubrics.id                      AS rubric_id,
         rubrics.peer_review_open_date   AS open_date,
         rubrics.reviewed_assignment_id  AS prompt_id,
         rubrics.passback_assignment_id  AS peer_review_assignment_id,
         count(DISTINCT peer_reviews.id) AS number_of_assigned_reviews
       FROM rubrics
         LEFT JOIN canvas_assignments ON rubrics.reviewed_assignment_id = canvas_assignments.id
         LEFT JOIN canvas_submissions ON canvas_assignments.id = canvas_submissions.assignment_id
         LEFT JOIN peer_reviews ON canvas_submissions.id = peer_reviews.submission_id
       WHERE course_id = %s
       GROUP BY rubric_id) AS total_reviews ON peer_review_assignments.id = total_reviews.peer_review_assignment_id
      LEFT JOIN (SELECT
                   criteria_by_rubric.rubric_id,
                   cast(sum(number_of_criteria = number_of_comments AND
                            number_of_comments IS NOT NULL)
                        AS SIGNED) AS number_of_completed_reviews
                 FROM
                   (SELECT
                      rubrics.id                  AS rubric_id,
                      rubrics.passback_assignment_id,
                      count(DISTINCT criteria.id) AS number_of_criteria
                    FROM rubrics
                      LEFT JOIN criteria ON rubrics.id = criteria.rubric_id
                    GROUP BY rubrics.id) AS criteria_by_rubric
                   LEFT JOIN (SELECT
                                rubric_id,
                                peer_review_id,
                                count(DISTINCT peer_review_comments.id) AS number_of_comments
                              FROM rubrics
                                LEFT JOIN criteria ON rubrics.id = criteria.rubric_id
                                LEFT JOIN canvas_assignments ON rubrics.reviewed_assignment_id = canvas_assignments.id
                                LEFT JOIN canvas_submissions ON canvas_assignments.id = canvas_submissions.assignment_id
                                LEFT JOIN peer_reviews ON canvas_submissions.id = peer_reviews.submission_id
                                LEFT JOIN peer_review_comments
                                  ON peer_reviews.id = peer_review_comments.peer_review_id AND
                                     criteria.id = peer_review_comments.criterion_id
                              WHERE peer_review_comments.id IS NOT NULL
                              GROUP BY rubric_id, peer_review_id
                              ORDER BY NULL) AS comments_by_rubric
                     ON criteria_by_rubric.rubric_id = comments_by_rubric.rubric_id
                 GROUP BY criteria_by_rubric.rubric_id) AS completed_reviews
        ON total_reviews.rubric_id = completed_reviews.rubric_id
      LEFT JOIN peer_review_distributions ON total_reviews.rubric_id = peer_review_distributions.rubric_id
    WHERE peer_review_assignments.id in %s and peer_review_assignments.is_peer_review_assignment IS TRUE;
    """

    @staticmethod
    def _format_details(data):
        for row in data:
            row['due_date'] = row['due_date'].strftime(API_DATE_FORMAT)
            if row.get('open_date'):
                row['open_date'] = row['open_date'].strftime(API_DATE_FORMAT)
            row['reviews_in_progress'] = row['reviews_in_progress'] == 1
        return data

    @classmethod
    def get(cls, course_id, assignment_ids):
        with connection.cursor() as cursor:
            cursor.execute(cls.query, [course_id, assignment_ids])
            data = fetchall_dicts(cursor)
        return cls._format_details(data)


class StudentDashboardStatus:
    @staticmethod
    def _make_review(peer_review):
        return {
            'review_id': peer_review.id,
            'submission_id': peer_review.submission.id,  # TODO remove this when review submission is ported to VueJS
            'review_is_complete': peer_review.review_is_complete
        }

    @staticmethod
    def _make_data(entry):
        prompt_id, peer_reviews = entry
        prompt_name = peer_reviews[0].submission.assignment.title
        due_date_utc = peer_reviews[0].submission.assignment.rubric_for_prompt.passback_assignment.due_date_utc
        return {
            'prompt_id':    prompt_id,
            'prompt_name':  prompt_name,
            'due_date_utc': due_date_utc,
        }

    @staticmethod
    def _make_assigned_prompt(entry):
        _, peer_reviews = entry
        prompt_data = StudentDashboardStatus._make_data(entry)
        prompt_data['reviews'] = sorted(map(StudentDashboardStatus._make_review, peer_reviews),
                                        key=lambda r: r['review_id'])
        return prompt_data

    @staticmethod
    def _make_completed_prompt(entry):

        def complete_review_pred(pr):
            return pr.review_is_complete

        _, peer_reviews = entry
        prompt_data = StudentDashboardStatus._make_data(entry)
        prompt_data['prompt_id'] = peer_reviews[0].submission.assignment.id
        prompt_data['rubric_id'] = peer_reviews[0].submission.assignment.rubric_for_prompt.id

        reviews_by_reviewer = groupby(lambda pr: pr.student_is_reviewer, peer_reviews)
        reviews_given = reviews_by_reviewer.get(True) or []
        reviews_received = reviews_by_reviewer.get(False) or []

        prompt_data['reviews'] = {
            'given': {
                'completed': sum(1 for _ in filter(complete_review_pred, reviews_given)),
                'total':     len(reviews_given)
            },
            'received': {
                'completed': sum(1 for _ in filter(complete_review_pred, reviews_received)),
                'total':     len(reviews_received)
            }
        }

        return prompt_data

    @staticmethod
    def _sort_and_format(data):
        sorted_data = sorted(data, key=lambda r: r['due_date_utc'])
        for review in sorted_data:
            review['due_date_utc'] = review['due_date_utc'].strftime(API_DATE_FORMAT)
        return sorted_data

    @staticmethod
    def _review_completion_status(qs):
        return qs.annotate(
                number_of_criteria=Subquery(
                    Criterion.objects.filter(rubric_id=OuterRef('submission__assignment__rubric_for_prompt__id'))
                        .values('rubric')
                        .annotate(count=Count('id'))
                        .values('count')
                )
            ) \
            .annotate(
                number_of_comments=Subquery(
                    PeerReviewComment.objects.filter(peer_review__id=OuterRef('id'))
                        .values('peer_review')
                        .annotate(count=Count('id'))
                        .values('count')
                )
            ) \
            .annotate(
                review_is_complete=Case(
                    When(number_of_comments=F('number_of_criteria'), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )

    @staticmethod
    def _unflatten(qs, filter_predicate, transform):
        return thread_last(qs,
                           (groupby, lambda pr: pr.submission.assignment_id),
                           (valfilter, lambda prs: some(filter_predicate, prs)),
                           (lambda d: d.items(),),
                           (map, transform),
                           (StudentDashboardStatus._sort_and_format,))

    @staticmethod
    def assigned_work(course_id, student_id):
        qs = PeerReview.objects.filter(student_id=student_id, submission__assignment__course__id=course_id) \
            .select_related('submission__assignment__rubric_for_prompt')
        qs = StudentDashboardStatus._review_completion_status(qs) \
            .order_by('submission__assignment_id', 'id')

        return StudentDashboardStatus._unflatten(
            qs,
            lambda pr: not pr.review_is_complete,
            StudentDashboardStatus._make_assigned_prompt
        )

    @staticmethod
    def completed_work(course_id, student_id):
        filter_query = \
            Q(submission__assignment__course__id=course_id) & \
            (Q(student_id=student_id) | Q(submission__author_id=student_id))
        qs = PeerReview.objects.filter(filter_query) \
            .annotate(
                student_is_reviewer=Case(
                    When(student_id=student_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        qs = StudentDashboardStatus._review_completion_status(qs)

        return StudentDashboardStatus._unflatten(
            qs,
            lambda pr: pr.review_is_complete,
            StudentDashboardStatus._make_completed_prompt
        )


class ReviewStatus:

    # TODO refactor to push load onto the DB
    # this method was pulled out of peer_review.views.core.AssignmentStatus
    @staticmethod
    def status_for_rubric(course_id, rubric_id, for_api=True):
        rubric = Rubric.objects.get(id=rubric_id)
        submissions = rubric.reviewed_assignment.canvas_submission_set.all()

        reviews = []
        sections = set()
        for submission in submissions:
            total_completed_num = submission.total_completed_by_a_student.count()
            completed_reviews_num = submission.num_comments_each_review_per_student       \
                                              .filter(completed__gte=rubric.num_criteria) \
                                              .count()

            total_received_num = submission.total_received_of_a_student.count()
            received_reviews_num = submission.num_comments_each_review_per_submission   \
                                             .filter(received__gte=rubric.num_criteria) \
                                             .count()

            if rubric.sections.all():
                rubric_sections_ids = rubric.sections.values_list('id', flat=True)
                author_sections = submission.author.sections.filter(
                    id__in=rubric_sections_ids,
                    course_id=course_id
                )
            else:
                author_sections = submission.author.sections.filter(course_id=course_id)

            for section in author_sections:
                sections.add(section)

            if for_api:
                author = {
                    'id': submission.author.id,
                    'name': submission.author.sortable_name
                }
                author_sections = [{'id': s.id, 'name': s.name} for s in author_sections]
            else:
                author = submission.author

            review = {
                'author':          author,
                'total_completed': total_completed_num,
                'completed':       completed_reviews_num,
                'total_received':  total_received_num,
                'received':        received_reviews_num,
                'sections':        author_sections,
            }
            if not for_api:
                review['json_sections'] = json.dumps(list(author_sections.values_list('id', flat=True)))

            reviews.append(review)

        sections = list(sections)
        sections.sort(key=lambda s: s.name)

        if for_api:
            sections = [{'id': s.id, 'name': s.name} for s in sections]
            due_date = rubric.passback_assignment.due_date_utc
            rubric = {
                'id': rubric.id,
                'peer_review_title': rubric.passback_assignment.title,
                'peer_review_due_date': due_date.strftime(API_DATE_FORMAT)
            }

        course = CanvasCourse.objects.get(id=course_id)
        return {
            'course_id': course.id,
            'title':     course.name,
            'reviews':   reviews,
            'rubric':    rubric,
            'sections':  sections
        }


# TODO refactor to be more ergonomic (this was lifted nearly verbatim from peer_review.views.core)
class RubricForm:

    @staticmethod
    def _get_unclaimed_assignments(course_id):
        query = Q(reviewed_assignment__course_id=course_id) | Q(revision_assignment__course_id=course_id)
        rubrics = Rubric.objects.filter(query)
        claimed_assignments = thread_last(rubrics,
                                          (map, lambda r: (r.reviewed_assignment_id, r.revision_assignment_id)),
                                          chain.from_iterable,
                                          unique,
                                          (filter, lambda i: i is not None))
        return CanvasAssignment.objects.filter(course_id=course_id, is_peer_review_assignment=False) \
                                       .exclude(id__in=claimed_assignments)

    @staticmethod
    def rubric_info(course, passback_assignment, fetched_assignments):
        try:
            existing_rubric = Rubric.objects.get(passback_assignment=passback_assignment)
        except Rubric.DoesNotExist:
            existing_rubric = None

        if existing_rubric:
            try:
                review_is_in_progress = PeerReviewDistribution.objects.get(rubric=existing_rubric) \
                    .is_distribution_complete
            except PeerReviewDistribution.DoesNotExist:
                review_is_in_progress = False
        else:
            review_is_in_progress = False

        existing_prompt = existing_rubric.reviewed_assignment if existing_rubric else None
        existing_revision = existing_rubric.revision_assignment if existing_rubric else None
        assignments = list(RubricForm._get_unclaimed_assignments(course.id))
        if existing_prompt:
            assignments.insert(0, existing_prompt)
        if existing_revision:
            assignments.insert(0, existing_revision)

        if existing_rubric:
            rubric_data = {
                'description': existing_rubric.description,
                'prompt_id': existing_prompt.id,
                'revision_id': existing_revision.id if existing_revision else None,
                'peer_review_due_date': passback_assignment.due_date_utc.strftime(API_DATE_FORMAT),
                'peer_review_open_date': existing_rubric.peer_review_open_date.strftime(API_DATE_FORMAT),
                'peer_review_open_date_is_prompt_due_date': existing_rubric.peer_review_open_date_is_prompt_due_date,
                'criteria': [
                    {'id': c.id, 'description': c.description}
                    for c in existing_rubric.criteria.all()
                ],
                'review_in_progress': review_is_in_progress
            }
        else:
            rubric_data = None

        return {
            'assignments': {a.id: a.title for a in assignments},
            'validation_info': {a.id: a.validation for a in fetched_assignments},
            'existing_rubric': rubric_data,
        }
