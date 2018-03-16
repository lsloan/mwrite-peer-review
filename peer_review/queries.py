from django.db import connection

from peer_review.util import fetchall_dicts


class ReviewDetails:
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
