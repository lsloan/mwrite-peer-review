from io import StringIO
from peer_review.canvas import retrieve, create, delete, submit_file


def delete_all_assignments(course_id):
    assignments = retrieve('assignments', course_id)
    for assignment in assignments:
        delete('assignment', course_id, assignment['id'])


def create_test_assignments(course_id, n=1):
    assignment_template = {
        'submission_types': ['online_upload'],
        'allowed_extensions': ['txt'],
        'published': True
    }
    created_assignments = []
    for i in range(1, n+1):
        assignment_template['name'] = 'Test Prompt %s' % i
        created_assignment = create('assignments', course_id, data={'assignment': assignment_template})
        created_assignments.append(created_assignment)
    return created_assignments


def submit_for_assignments(course_id, assignments, users):
    for assignment in assignments:
        for user in users:
            base = '%s for %s' % (assignment['name'], user['name'])
            filename = base.replace(' ', '_') + '.txt'
            contents = StringIO(base)
            submit_file(user['token'], course_id, assignment['id'], filename, contents)
