import os
import logging
import requests
from zipfile import ZipFile
from toolz.dicttoolz import dissoc
from toolz.functoolz import thread_last
from toolz.itertoolz import unique, remove
from django.db import transaction
from django.conf import settings
from django.utils.dateparse import parse_datetime
from peer_review.util import to_camel_case
from peer_review.canvas import retrieve
from peer_review.models import CanvasAssignment, CanvasSection, CanvasStudent, CanvasCourse, CanvasSubmission, Rubric

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
    def json_default(validation):
        return {to_camel_case(k): v for k, v in validation.__dict__.items()}


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


def _convert_assignment(assignment):
    course_id = assignment['course_id']
    assignment_id = assignment['id']
    overrides = retrieve('assignment-overrides', course_id, assignment_id) if assignment['has_overrides'] else None
    due_date_utc, number_of_due_dates = _due_dates_from_overrides(assignment, overrides)

    sections = None
    section_name = None
    if overrides:
        sections = thread_last(overrides,
                               (map, lambda o: o.get('course_section_id')),
                               (remove, lambda o: o is None),
                               list)
        if sections and len(sections) == 1:
            section_name = retrieve('section', course_id, sections[0])['name']

    validation = AssignmentValidation(submission_upload_type=assignment.get('submission_types'),
                                      allowed_extensions=assignment.get('allowed_extensions'),
                                      due_date_utc=due_date_utc,
                                      number_of_due_dates=number_of_due_dates,
                                      section_name=section_name,
                                      number_of_sections=len(sections) if sections else 0)
    return CanvasAssignment(id=assignment_id,
                            course_id=course_id,
                            title=assignment['name'],
                            due_date_utc=due_date_utc,
                            is_peer_review_assignment=_is_peer_review_assignment(assignment),
                            validation=validation)


def persist_course(course_id):
    raw_course = retrieve('course', course_id)
    course, _ = CanvasCourse.objects.get_or_create(defaults={
        'id': course_id,
        'name': raw_course['name']
    })
    return course


def persist_assignments(course_id):
    canvas_assignments = retrieve('assignments', course_id)
    assignments = [_convert_assignment(canvas_assignment) for canvas_assignment in canvas_assignments]
    for assignment in assignments:
        if not assignment.is_peer_review_assignment:
            try:
                rubric = CanvasAssignment.objects.get(id=assignment.id).rubric_for_prompt
                if rubric.peer_review_open_date_is_prompt_due_date:
                    if assignment.due_date_utc:
                        rubric.peer_review_open_date = assignment.due_date_utc
                        rubric.save()
                    else:
                        log.error(
                            'Rubric %d has peer review open date set to prompt %d due date, but this prompt has'
                            'no due date!' % (rubric.id, assignment.id)
                        )
                else:
                    if rubric.peer_review_open_date < assignment.due_date_utc:
                        log.warning('Prompt %d has a due date later than rubric %d\'s peer review open date' %
                                    (assignment.id, rubric.id))
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
    return CanvasStudent(id=raw_student['id'],
                         username=raw_student['login_id'],
                         full_name=raw_student['name'],
                         sortable_name=raw_student['sortable_name'])


def persist_students(course_id):
    raw_students = retrieve('students', course_id)
    enrollments_by_student_id = {s['id']: s['enrollments'] for s in raw_students}
    students = list(map(_convert_student, raw_students))

    with transaction.atomic():
        for student in students:
            student.save()
            for enrollment in enrollments_by_student_id[student.id]:
                student.sections.add(CanvasSection.objects.get(id=enrollment['course_section_id']))


def _download_single_attachment(destination, attachment):
    attachment_response = requests.get(attachment['url'])
    attachment_response.raise_for_status()
    attachment_filename = '%d_%s' % (attachment['id'], attachment['filename'])
    attachment_path = os.path.join(destination, attachment_filename)
    with open(attachment_path, 'wb') as attachment_file:
        attachment_file.write(attachment_response.content)
    return attachment_filename


def _download_multiple_attachments(destination, submission):
    submission_id_str = str(submission['id'])
    temp_directory_path = os.path.join(settings.MEDIA_ROOT, 'temporary', submission_id_str)
    os.makedirs(temp_directory_path, exist_ok=True)
    for attachment in submission['attachments']:
        _download_single_attachment(temp_directory_path, attachment)
    attachment_archive_filename = '%d_submissions.zip' % submission['id']
    attachment_archive_full_path = os.path.join(destination, attachment_archive_filename)
    log.info('dest = %s', destination)
    log.info('path = %s', attachment_archive_full_path)
    with ZipFile(attachment_archive_full_path, 'w') as archive_file:
        for _, _, files in os.walk(temp_directory_path):
            for fn in files:
                archive_file.write(os.path.join(temp_directory_path, fn),
                                   arcname=os.path.join(submission_id_str, fn))
    return attachment_archive_filename


def _convert_submission(raw_submission, filename):
    return {
        'id': raw_submission['id'],
        'author_id': raw_submission['user_id'],
        'assignment_id': raw_submission['assignment_id'],
        'filename': filename
    }


def _download_submission(raw_submission):
    attachments = raw_submission['attachments']
    destination = os.path.join(settings.MEDIA_ROOT, 'submissions')
    os.makedirs(destination, exist_ok=True)
    if len(attachments) > 1:
        filename = _download_multiple_attachments(destination, raw_submission)
    else:
        filename = _download_single_attachment(destination, raw_submission['attachments'][0])
    return _convert_submission(raw_submission, filename)


def persist_submissions(assignment):
    thread_last(retrieve('submissions', assignment.course.id, assignment.id),
                (remove, lambda s: s['workflow_state'] == 'unsubmitted'),
                (remove, lambda s: s.get('attachments') is None),
                (map, lambda s: _download_submission(s)),
                (map, lambda s: CanvasSubmission.objects.update_or_create(id=s['id'], defaults=dissoc(s, 'id'))),
                list)
