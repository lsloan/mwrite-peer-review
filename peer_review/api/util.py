import logging

import dateutil.parser
from django.core.exceptions import PermissionDenied

from peer_review.util import some
from peer_review.exceptions import APIException
from peer_review.etl import AssignmentValidation
from peer_review.models import CanvasAssignment, Criterion, PeerReview


LOGGER = logging.getLogger(__name__)


def raise_if_not_current_user(request, user_id):
    logged_in_user_id = request.session['lti_launch_params']['custom_canvas_user_id']
    if logged_in_user_id != user_id:
        LOGGER.warning('User %s tried to access information for user %s without permission'
                    % (logged_in_user_id, user_id))
        raise PermissionDenied


def raise_if_peer_review_not_given_to_student(request, student_id, peer_review_id):
    if not PeerReview.objects.filter(id=peer_review_id, submission__author_id=student_id).exists():
        logged_in_user_id = request.session['lti_launch_params']['custom_canvas_user_id']
        LOGGER.warning('User %s tried to submit an invalid peer review evaluation for user %s and peer review %s'
                    % (logged_in_user_id, student_id, peer_review_id))
        raise PermissionDenied


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

    peer_review_open_date = get_date_param_or_400('peer_review_open_date', params)
    peer_review_evaluation_due_date = get_date_param_or_400('peer_review_evaluation_due_date', params)

    pr_open_date_is_prompt_due_date = get_boolean_param_or_400('peer_review_open_date_is_prompt_due_date', params)
    peer_review_evaluation_is_mandatory = get_boolean_param_or_400('peer_review_evaluation_is_mandatory', params)

    return {
        'prompt_assignment': prompt_assignment,
        'peer_review_assignment': passback_assignment,
        'revision_assignment': revision_assignment,
        'rubric_description': rubric_description,
        'criteria': criteria,
        'peer_review_open_date': peer_review_open_date,
        'peer_review_evaluation_due_date': peer_review_evaluation_due_date,
        'peer_review_open_date_is_prompt_due_date': pr_open_date_is_prompt_due_date,
        'peer_review_evaluation_is_mandatory': peer_review_evaluation_is_mandatory
    }

def get_boolean_param_or_400(key_name, params):
    if key_name not in params:
        error = 'Missing {} flag.'.format(key_name)
        raise APIException(data={'error': error}, status_code=400)
    return params[key_name]

def get_date_param_or_400(key_name, params):
    if key_name not in params or not params[key_name].strip():
        raise APIException(data={'error': 'Missing {}.'.format(key_name)}, status_code=400)
    try:
        return dateutil.parser.parse(params[key_name])
    except ValueError:
        error = '{} should be a valid ISO 8601 date.'.format(key_name)
        raise APIException(data={'error': error}, status_code=400)