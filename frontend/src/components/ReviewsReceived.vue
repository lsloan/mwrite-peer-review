<template>
    <div>
        <div class="controls">
            <span>View by:</span>
            <div class="control-button-container">
                <button
                    :class="{'control-button': true, 'control-button--active': viewBy === 'reviewer'}"
                    @click="viewBy = 'reviewer'">
                    Student
                </button>
                <button
                    :class="{'control-button': true, 'control-button--active': viewBy === 'criterion'}"
                    @click="viewBy = 'criterion'">
                    Criteria
                </button>
            </div>
        </div>
        <div class="reviews-body">
            <keep-alive>
                <reviews-by-reviewer v-if="viewBy === 'reviewer'" :data="data" :allow-evaluation="true"/>
                <reviews-by-criterion v-else-if="viewBy === 'criterion'" :data="data"/>
            </keep-alive>
        </div>
    </div>
</template>

<script>
import ReviewsByReviewer from '@/components/ReviewsByReviewer';
import ReviewsByCriterion from '@/components/ReviewsByCriterion';
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

const denormalizers = {
  reviewer: partial(denormalize, [reviewerIdentity, makeReviewerEntry]),
  criterion: partial(denormalize, [criterionIdentity, makeCriterionEntry])
};

export default {
  name: 'reviews-received',
  props: ['student-id', 'rubric-id'],
  components: {ReviewsByReviewer, ReviewsByCriterion},
  data() {
    return {
      viewBy: 'reviewer',
      unfilteredData: null
    };
  },
  computed: {
    data() {
      if(this.unfilteredData) {
        return denormalizers[this.viewBy](this.unfilteredData.entries);
      }
    }
  },
  methods: {
    setData(data) {
      this.unfilteredData = data;
      this.$emit('title-resolved', this.unfilteredData.title);
    }
  },
  mounted() {
    const courseId = this.$store.state.userDetails.courseId;
    this.$api.get('/course/{}/reviews/student/{}/received/{}', courseId, this.studentId, this.rubricId)
      .then(response => this.setData(response.data));
  }
};
</script>

<style scoped>
    .reviews-body {
        padding: 15px 20px;
    }

    .controls {
        padding: 10px 20px;
        background-color: #5D72C8;
        height: 32px;
        line-height: 32px;
        color: white;
        font-size: 0;
    }

    .controls > span {
        font-size: 14px;
    }

    .control-button-container {
        display: inline;
        margin-left: 8px;
    }

    .control-button {
        border: 1px solid white;
        background-color: #5D72C8;
        color: white;
        padding: 5px 15px 6px 15px;
    }

    .control-button--active {
        background-color: white;
        color: black;
    }

    .control-button:focus {
        outline: 0;
    }

</style>
