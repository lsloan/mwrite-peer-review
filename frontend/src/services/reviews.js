import {sortBy} from 'ramda';

const makeReviewerCommentEntry = comment => ({
  id: comment.commentId,
  criterionId: comment.criterionId,
  heading: comment.criterion,
  content: comment.comment
});

const makeCriterionCommentEntry = comment => ({
  id: comment.commentId,
  reviewerId: comment.reviewerId,
  heading: `Student ${comment.reviewerId}`,
  content: comment.comment
});

const makeReviewerEntry = comments => {
  const {reviewerId, peerReviewId, evaluationSubmitted} = comments[0];
  const reviewerNumber = parseInt(reviewerId);
  return {
    id: reviewerNumber,
    title: `Student ${reviewerNumber}`,
    peerReviewId: peerReviewId,
    evaluationSubmitted: evaluationSubmitted,
    entries: sortBy(c => c.criterionId, comments.map(makeReviewerCommentEntry))
  };
};

const makeCriterionEntry = comments => {
  const {criterionId, criterion} = comments[0];
  const criterionNumber = parseInt(criterionId);
  return {
    id: criterionNumber,
    title: `Criterion ${criterionNumber}`,
    criterion: criterion,
    entries: sortBy(c => c.reviewerId, comments.map(makeCriterionCommentEntry))
  };
};

export const conversions = {
  reviewer: makeReviewerEntry,
  criterion: makeCriterionEntry
};
