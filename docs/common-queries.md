# Common Queries

These are some common queries used for various debugging tasks.

## All Comments Given and Received

```sql
select
  prompts.course_id            as 'Course',
  prompts.title                as 'Prompt',
  authors.sortable_name        as 'Author',
  reviewers.sortable_name      as 'Reviewer',
  criteria.description         as 'Criterion',
  peer_review_comments.comment as 'Comment'
from peer_review_comments
  left join peer_reviews on peer_review_comments.peer_review_id = peer_reviews.id
  left join canvas_students as reviewers on peer_reviews.student_id = reviewers.id
  left join canvas_submissions on peer_reviews.submission_id = canvas_submissions.id
  left join canvas_assignments as prompts on canvas_submissions.assignment_id = prompts.id
  left join rubrics on prompts.id = rubrics.reviewed_assignment_id
  left join canvas_students as authors on canvas_submissions.author_id = authors.id
  left join criteria on peer_review_comments.criterion_id = criteria.id
order by prompts.id, authors.sortable_name, reviewers.sortable_name, peer_review_comments.criterion_id;
```

## Rubrics And Prompts

```sql
select
    rubrics.id                     as rubric_id,
    rubrics.peer_review_open_date,
    rubrics.reviewed_assignment_id as prompt_id,
    peer_review_distributions.is_distribution_complete,
    canvas_courses.id              as course_id,
    canvas_courses.name            as course_title
from rubrics
    left join peer_review_distributions on peer_review_distributions.rubric_id = rubrics.id
    left join canvas_assignments on canvas_assignments.id = rubrics.reviewed_assignment_id
    left join canvas_courses on canvas_courses.id = canvas_assignments.course_id
order by peer_review_open_date desc;
```
