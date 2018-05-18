import dateutil.parser

from peer_review.util import some
from peer_review.exceptions import APIException
from peer_review.etl import AssignmentValidation
from peer_review.models import CanvasAssignment, Criterion


def merge_validations(data, validations):
    for row in data:
        validation_info = validations.get(row['prompt_id'])
        if validation_info:
            validation_info_dict = AssignmentValidation.json_default(validation_info)
            row['validation_info'] = validation_info_dict
        else:
            row['validation_info'] = None

    return data


def validate_rubric(course_id, params):
    passback_assignment_id = params.get('peer_review_assignment_id')
    if not passback_assignment_id:
        raise APIException(data={'error': 'Missing peer review assignment.'}, status_code=400)
    try:
        passback_assignment = CanvasAssignment.objects.get(id=passback_assignment_id)
        if passback_assignment.course_id != course_id:
            error = 'The requested peer review assignment is not part of the specified course.'
            raise APIException(data={'error': error}, status_code=403)
    except CanvasAssignment.DoesNotExist:
        error = 'The requested peer review assignment does not exist.'
        raise APIException(data={'error': error}, status_code=400)

    prompt_assignment_id = params.get('prompt_id')
    if not prompt_assignment_id:
        raise APIException(data={'error': 'Missing prompt assignment.'}, status_code=400)
    try:
        prompt_assignment = CanvasAssignment.objects.get(id=prompt_assignment_id)
        if prompt_assignment.course_id != course_id:
            error = 'The requested prompt is not part of the specified course.'
            raise APIException(data={'error': error}, status_code=403)
    except CanvasAssignment.DoesNotExist:
        error = 'The requested prompt does not exist.'
        raise APIException(data={'error': error}, status_code=400)

    revision_assignment_id = params.get('revision_id')
    if revision_assignment_id:
        try:
            revision_assignment = CanvasAssignment.objects.get(id=revision_assignment_id)
            if revision_assignment.course_id != course_id:
                error = 'The requested revision is not part of the specified course.'
                raise APIException(data={'error': error}, status_code=403)
        except CanvasAssignment.DoesNotExist:
            error = 'The requested revision does not exist.'
            raise APIException(data={'error': error}, status_code=400)   
    else:
        revision_assignment = None

    rubric_description = params['description'].strip() if 'description' in params else None
    if not rubric_description:
        raise APIException(data={'error': 'Missing or blank rubric description.'}, status_code=400)

    if not params.get('criteria'):
        raise APIException(data={'error': 'Missing criteria.'}, status_code=400)
    if some(lambda c: not c.strip(), params['criteria']):
        raise APIException(data={'error': 'One or more blank criteria submitted.'}, status_code=400)
    criteria = [Criterion(description=criterion) for criterion in params['criteria']]

    if 'peer_review_open_date' not in params or not params['peer_review_open_date'].strip():
        raise APIException(data={'error': 'Missing peer review open date.'}, status_code=400)
    try:
        peer_review_open_date = dateutil.parser.parse(params['peer_review_open_date'])
    except ValueError:
        error = 'Peer review open date should be a valid ISO 8601 date.'
        raise APIException(data={'error': error}, status_code=400)

    if 'peer_review_open_date_is_prompt_due_date' not in params:
        error = 'Missing peer review open date is prompt due date flag.'
        raise APIException(data={'error': error}, status_code=400)
    pr_open_date_is_prompt_due_date = params['peer_review_open_date_is_prompt_due_date']

    return {
        'prompt_assignment': prompt_assignment,
        'peer_review_assignment': passback_assignment,
        'revision_assignment': revision_assignment,
        'rubric_description': rubric_description,
        'criteria': criteria,
        'peer_review_open_date': peer_review_open_date,
        'peer_review_open_date_is_prompt_due_date': pr_open_date_is_prompt_due_date
    }
