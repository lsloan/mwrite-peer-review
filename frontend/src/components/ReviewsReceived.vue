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
                <reviews-by-reviewer v-if="viewBy === 'reviewer'" :data="data"/>
                <reviews-by-criterion v-else-if="viewBy === 'criterion'" :data="data"/>
            </keep-alive>
        </div>
    </div>
</template>

<script>
import ReviewsByReviewer from '@/components/ReviewsByReviewer';
import ReviewsByCriterion from '@/components/ReviewsByCriterion';
import {groupBy} from 'ramda';

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
        if(this.viewBy === 'reviewer') {
          const commentsByReviewer = groupBy(entry => entry.reviewerId, this.unfilteredData.entries);
          return Object.entries(commentsByReviewer).map(entry => {
            const [reviewerId, comments] = entry;
            return {
              id: reviewerId,
              title: `Student ${comments[0].reviewerId + 1}`,
              entries: comments.map(c => ({id: c.commentId, heading: c.criterion, content: c.comment})) // TODO sort comments?
            };
          });
        }
        else if(this.viewBy === 'criterion') {
          const commentsByCriterion = groupBy(entry => entry.criterionId, this.unfilteredData.entries);
          return Object.entries(commentsByCriterion).map(entry => {
            const [criterionId, comments] = entry;
            return {
              id: criterionId,
              title: `Criterion ${comments[0].criterionId + 1}`,
              entries: comments.map(c => ({id: c.commentId, reviewerName: `Student ${c.reviewerId + 1}`, text: c.comment}))
            };
          });
        }
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
    .reviews-body, .controls {
        padding: 10px 20px;
    }

    .controls {
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

</style>
