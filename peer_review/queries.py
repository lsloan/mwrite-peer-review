from toolz.itertoolz import groupby
from toolz.dicttoolz import valfilter
from toolz.functoolz import thread_last
from django.db import connection
from django.db.models import BooleanField, Subquery, OuterRef, Count, Case, When, Value, F, Q

from peer_review.util import some, fetchall_dicts
from peer_review.models import PeerReview, Criterion, PeerReviewComment


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
            row['due_date'] = row['due_date'].strftime('%Y-%m-%d %H:%M:%SZ')
            if row.get('open_date'):
                row['open_date'] = row['open_date'].strftime('%Y-%m-%d %H:%M:%SZ')
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
            review['due_date_utc'] = review['due_date_utc'].strftime('%Y-%m-%d %H:%M:%SZ')
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
    def assigned_work(student_id):
        qs = PeerReview.objects.filter(student_id=student_id) \
            .select_related('submission__assignment__rubric_for_prompt')
        qs = StudentDashboardStatus._review_completion_status(qs) \
            .order_by('submission__assignment_id', 'id')

        return StudentDashboardStatus._unflatten(
            qs,
            lambda pr: not pr.review_is_complete,
            StudentDashboardStatus._make_assigned_prompt
        )

    @staticmethod
    def completed_work(student_id):
        qs = PeerReview.objects.filter(Q(student_id=student_id) | Q(submission__author_id=student_id)) \
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
