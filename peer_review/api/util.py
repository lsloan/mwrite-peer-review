from toolz.functoolz import thread_last

from peer_review.etl import AssignmentValidation


def merge_validations(data, validations):
    for row in data:
        validation_info = validations.get(row['prompt_id'])
        if validation_info:
            validation_info_dict = AssignmentValidation.json_default(validation_info)
            row['validation_info'] = validation_info_dict
        else:
            row['validation_info'] = None

    return data
