import {partial, sortBy, groupBy} from 'ramda';

const denormalize = (identity, transform, data) => {
  const groups = groupBy(identity, data);
  const entries = Object.entries(groups).map(transform);
  return sortBy(identity, entries);
};

const reviewerIdentity = entry => entry.reviewerId;
const criterionIdentity = entry => entry.criterionId;

const makeReviewerCommentEntry = comment => ({
  id: comment.commentId,
  criterionId: comment.criterionId,
  heading: comment.criterion,
  content: comment.comment
});

const makeCriterionCommentEntry = comment => ({
  id: comment.commentId,
  reviewerId: comment.reviewerId,
  heading: `Student ${comment.reviewerId + 1}`,
  content: comment.comment
});

const makeReviewerEntry = entry => {
  const [reviewerIdStr, comments] = entry;
  const reviewerId = parseInt(reviewerIdStr);
  return {
    id: reviewerId,
    title: `Student ${comments[0].reviewerId + 1}`,
    peerReviewId: comments[0].peerReviewId,
    evaluationSubmitted: comments[0].evaluationSubmitted,
    entries: sortBy(c => c.criterionId, comments.map(makeReviewerCommentEntry))
  };
};

const makeCriterionEntry = entry => {
  const [criterionIdStr, comments] = entry;
  const criterionId = parseInt(criterionIdStr);
  return {
    id: criterionId,
    title: `Criterion ${criterionId + 1}`,
    criterion: comments[0].criterion,
    entries: sortBy(c => c.reviewerId, comments.map(makeCriterionCommentEntry))
  };
};

export const denormalizers = {
  reviewer: partial(denormalize, [reviewerIdentity, makeReviewerEntry]),
  criterion: partial(denormalize, [criterionIdentity, makeCriterionEntry])
};
