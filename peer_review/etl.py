import os
import logging
import requests
from zipfile import ZipFile
from functools import partial

from toolz.dicttoolz import dissoc
from toolz.functoolz import thread_last, memoize
from toolz.itertoolz import unique, remove
from django.db import transaction
from django.conf import settings
from django.utils.dateparse import parse_datetime

from peer_review.util import to_camel_case
from peer_review.canvas import retrieve
from peer_review.models import CanvasAssignment, CanvasSection, CanvasStudent, CanvasCourse, CanvasSubmission, Rubric, \
    JobLog

log = logging.getLogger(__name__)


class AssignmentValidation:
    def __init__(self, **kwargs):
        self.submission_upload_type = kwargs.get('submission_upload_type')
        self.allowed_submission_file_extensions = kwargs.get('allowed_extensions')
        if kwargs.get('due_date_utc') is not None:
            self.due_date_utc = kwargs.get('due_date_utc').isoformat()
        else:
            self.local_due_date = None
        self.number_of_due_dates = kwargs.get('number_of_due_dates')
        self.section_name = kwargs.get('section_name')
        self.number_of_sections = kwargs.get('number_of_sections')

    @staticmethod
    def json_default(validation, camel_case=True):
        def key_transform(key):
            if camel_case:
                return to_camel_case(key)
            else:
                return key
        return {key_transform(k): v for k, v in validation.__dict__.items()}


def _due_dates_from_overrides(assignment, overrides):
    if assignment.get('due_at') is not None:
        due_date_utc = parse_datetime(assignment['due_at'])
    elif overrides and len(overrides) == 1 and overrides[0].get('due_at'):
        due_date_utc = parse_datetime(overrides[0]['due_at'])
    else:
        due_date_utc = None
        number_of_overrides = len(overrides) if overrides else 0
        log.warning('Assignment %d has no due date and %d overrides!' % (assignment['id'], number_of_overrides))
    if due_date_utc:
        number_of_due_dates = 1
    elif overrides:
        number_of_due_dates = thread_last(overrides, (map, lambda o: o['due_at']), unique, list, len)
    else:
        number_of_due_dates = 0
    return due_date_utc, number_of_due_dates


def _is_peer_review_assignment(assignment):
    return 'external_tool_tag_attributes' in assignment and \
           'url' in assignment['external_tool_tag_attributes'] and \
           settings.APP_HOST in assignment['external_tool_tag_attributes']['url']


def _convert_assignment(section_name_getter, assignment):
    course_id = assignment['course_id']
    assignment_id = assignment['id']
    due_date_utc, number_of_due_dates = _due_dates_from_overrides(assignment, assignment.get('overrides'))

    section_ids = None
    section_name = None
    if 'overrides' in assignment:
        section_ids = thread_last(assignment['overrides'],
                                  (map, lambda o: o.get('course_section_id')),
                                  (remove, lambda o: o is None),
                                  list)
        if section_ids and len(section_ids) == 1:
            section_name = section_name_getter(section_ids[0])

    validation = AssignmentValidation(submission_upload_type=assignment.get('submission_types'),
                                      allowed_extensions=assignment.get('allowed_extensions'),
                                      due_date_utc=due_date_utc,
                                      number_of_due_dates=number_of_due_dates,
                                      section_name=section_name,
                                      number_of_sections=len(section_ids) if section_ids else 0)
    return CanvasAssignment(id=assignment_id,
                            course_id=course_id,
                            title=assignment['name'],
                            due_date_utc=due_date_utc,
                            is_peer_review_assignment=_is_peer_review_assignment(assignment),
                            validation=validation)


def persist_course(course_id):
    raw_course = retrieve('course', course_id)
    course, _ = CanvasCourse.objects.get_or_create(
        id=course_id,
        defaults={
            'name': raw_course['name']
        }
    )
    return course


def persist_assignments(course_id):
    section_name_getter = memoize(lambda section_id: retrieve('section', course_id, section_id)['name'])
    assignment_converter = partial(_convert_assignment, section_name_getter)

    canvas_assignments = retrieve('assignments', course_id)
    assignments = [assignment_converter(canvas_assignment) for canvas_assignment in canvas_assignments]

    for assignment in assignments:
        if not assignment.is_peer_review_assignment:
            try:
                rubric = CanvasAssignment.objects.get(id=assignment.id).rubric_for_prompt
                if rubric.peer_review_open_date_is_prompt_due_date:
                    if assignment.due_date_utc:
                        rubric.peer_review_open_date = assignment.due_date_utc
                        rubric.save()
                    else:
                        log.warning(
                            'Rubric (%d) for course (%d) has peer review open date set to prompt "%s" (%d) due date, '
                            'but prompt has no due date!' %
                            (rubric.id, course_id, assignment.title, assignment.id)
                        )
                else:
                    if assignment.due_date_utc is None:
                        log.warning('Prompt assignment "%s" (%d) for course (%d) does not have a due date '
                                    '(rubric (%d))' %
                                    (assignment.title, assignment.id, course_id, rubric.id))
                        continue

                    if rubric.peer_review_open_date is None:
                        log.warning('Rubric (%d) for course (%d) does not have a due date (assignment "%s" (%d))' %
                                    (rubric.id, course_id, assignment.title, assignment.id))
                        continue

                    if rubric.peer_review_open_date < assignment.due_date_utc:
                        log.warning('Prompt "%s" (%d) for course (%d) has a due date later than rubric (%d)\'s '
                                    'peer review open date' %
                                    (assignment.title, assignment.id, course_id, rubric.id))
            except CanvasAssignment.DoesNotExist:
                pass
            except Rubric.DoesNotExist:
                pass
        assignment.save()
    return assignments


def _convert_section(section):
    return CanvasSection(id=section['id'], name=section['name'], course_id=section['course_id'])


def persist_sections(course_id):
    raw_sections = retrieve('sections', course_id)
    sections = list(map(_convert_section, raw_sections))
    with transaction.atomic():
        for section in sections:
            section.save()


def _convert_student(raw_student):
    student_id = raw_student['id']
    if 'login_id' in raw_student:
        username = raw_student['login_id']
    else:
        username = str(student_id)

    return CanvasStudent(
        id=student_id,
        username=username,
        full_name=raw_student['name'],
        sortable_name=raw_student['sortable_name']
    )


def persist_students(course_id):
    course = CanvasCourse.objects.get(id=course_id)
    raw_students = retrieve('students', course_id)
    enrollments_by_student_id = {s['id']: s['enrollments'] for s in raw_students}
    students = list(map(_convert_student, raw_students))

    with transaction.atomic():
        for student in students:
            student.save()
            student.courses.add(course)
            for enrollment in enrollments_by_student_id[student.id]:
                student.sections.add(CanvasSection.objects.get(id=enrollment['course_section_id']))


def _download_single_attachment(destination, attachment, useFaultTolerance: bool):
    """
    Try to download an attachment and save to destination directory.

    :return: Tuple of strings containing filename and error message (or None)
    """
    attachment_filename = '%d_%s' % (attachment['id'], attachment['filename'])
    log.info('Downloading "%s"...' % (attachment_filename))
    attachment_response = requests.get(attachment['url'])

    try:
        if (settings.DEBUG) and (settings.TOLERANCE_TEST_ERRONEOUS_FILENAME == attachment['filename']):
            raise Exception('got "%s" test file (see "MPR_TOLERANCE_TEST_ERRONEOUS_FILENAME" in environment)' %
                            (settings.TOLERANCE_TEST_ERRONEOUS_FILENAME))
        attachment_response.raise_for_status()
    except Exception as requestException:
        if (not useFaultTolerance):
            raise
        message = 'Trouble downloading "%s": %s' % (attachment_filename, requestException)
        JobLog.addMessage(message)
        log.warning(message)
        return (attachment_filename, str(requestException))

    attachment_path = os.path.join(destination, attachment_filename)
    with open(attachment_path, 'wb') as attachment_file:
        attachment_file.write(attachment_response.content)
    return (attachment_filename, None)


def _download_multiple_attachments(destination, submission, useFaultTolerance: bool):
    """
    Try to download multiple attachments and save to ZIP file in destination directory.

    :return: Tuple of strings containing filename and error message (or None)
    """
    submission_id_str = str(submission['id'])
    temp_directory_path = os.path.join(settings.MEDIA_ROOT, 'temporary', submission_id_str)
    os.makedirs(temp_directory_path, exist_ok=True)
    error = None
    for attachment in submission['attachments']:
        (filename, error) = _download_single_attachment(temp_directory_path, attachment, useFaultTolerance)
        if (error):
            break
    attachment_archive_filename = '%d_submissions.zip' % submission['id']
    attachment_archive_full_path = os.path.join(destination, attachment_archive_filename)
    with ZipFile(attachment_archive_full_path, 'w') as archive_file:
        for _, _, files in os.walk(temp_directory_path):
            for fn in files:
                archive_file.write(os.path.join(temp_directory_path, fn),
                                   arcname=os.path.join(submission_id_str, fn))
    return (attachment_archive_filename, error)


def _convert_submission(raw_submission, filename, error):
    submissionData = {
        'id': raw_submission['id'],
        'author_id': raw_submission['user_id'],
        'assignment_id': raw_submission['assignment_id'],
        'filename': filename
    }

    if (error is not None):
        submissionData['error'] = error

    return submissionData


def _download_submission(raw_submission, useFaultTolerance: bool):
    log.info('Downloading submission (%d) file(s) from student (%d) for assignment (%d)...' %
             (raw_submission['id'], raw_submission['user_id'], raw_submission['assignment_id']))
    attachments = raw_submission['attachments']
    destination = os.path.join(settings.MEDIA_ROOT, 'submissions')
    os.makedirs(destination, exist_ok=True)
    if len(attachments) > 1:
        (filename, error) = _download_multiple_attachments(destination, raw_submission, useFaultTolerance)
    else:
        (filename, error) = _download_single_attachment(destination, raw_submission['attachments'][0], useFaultTolerance)
    return _convert_submission(raw_submission, filename, error)


def persist_submissions(assignment: CanvasAssignment, useFaultTolerance: bool):
    log.info('Persisting submissions for course (%d), assignment (%d)...' %
             (assignment.course.id, assignment.id))

    courseStudentIds = CanvasStudent.objects \
        .filter(courses=assignment.course) \
        .values_list('id', flat=True)

    submissionData: list = thread_last(retrieve('submissions', assignment.course.id, assignment.id),
                                       (remove, lambda s: s['user_id'] not in courseStudentIds),
                                       (remove, lambda s: s['workflow_state'] == 'unsubmitted'),
                                       (remove, lambda s: s.get('attachments') is None),
                                       (map, lambda s: _download_submission(s, useFaultTolerance)),
                                       list)

    if (len(submissionData) == 0):
        message = ('Unable to persist submissions for course (%d), assignment (%d).'
                   '  No submissions were found.') % \
                  (assignment.course.id, assignment.id)
        log.warning(message)
        return

    errors: list = thread_last(
        filter(lambda s: s.get('error') is not None, submissionData),
        list)

    log.info('Attempted (%d) submission downloads for course (%d), assignment (%d), with (%d) error(s).' %
             (len(submissionData), assignment.course.id, assignment.id, len(errors)))

    if (useFaultTolerance is True):
        errorRate: float = len(errors) / len(submissionData)

        if (errorRate > settings.TOLERANCE_RATE):
            message = ('Persisting submissions for course (%d), assignment (%d), failed.'
                       '  Error rate (%f) exceeds fault tolerance (%f).') % \
                      (assignment.course.id, assignment.id, errorRate, settings.TOLERANCE_RATE)
            JobLog.addMessage(message)
            raise Exception(message)
        else:
            message = ('Persisting submissions for course (%d), assignment (%d), successful.'
                       '  Error rate (%f) within fault tolerance (%f).') % \
                      (assignment.course.id, assignment.id, errorRate, settings.TOLERANCE_RATE)
            log.info(message)

    thread_last(submissionData,
                (remove, lambda s: s.get('error') is not None),
                (map, lambda s: CanvasSubmission.objects.update_or_create(id=s['id'], defaults=dissoc(s, 'id'))),
                list)

    log.info('Persisting submissions for course (%d), assignment (%d) complete.' %
             (assignment.course.id, assignment.id))
