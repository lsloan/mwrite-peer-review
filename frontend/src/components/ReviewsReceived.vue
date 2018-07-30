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
                <reviews-by-reviewer v-if="viewBy === 'reviewer'" :data="reviews"/>
                <reviews-by-criterion v-else-if="viewBy === 'criterion'" :data="reviews"/>
            </keep-alive>
        </div>
    </div>
</template>

<script>
import * as R from 'ramda';

import {conversions} from '@/services/reviews';
import ReviewsByReviewer from '@/components/ReviewsByReviewer';
import ReviewsByCriterion from '@/components/ReviewsByCriterion';

export default {
  name: 'reviews-received',
  props: ['student-id', 'rubric-id'],
  components: {ReviewsByReviewer, ReviewsByCriterion},
  data() {
    return {
      viewBy: 'reviewer'
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    commentsForRubric() {
      const rubricId = parseInt(this.rubricId);
      const commentsForRubric = this.$store.getters.commentsBy.rubric[rubricId];
      return commentsForRubric ? commentsForRubric[this.viewBy] : {};
    },
    promptTitle() {
      return Object.values(this.commentsForRubric)[0][0].promptTitle;
    },
    reviews() {
      const convertedReviews = R.map(conversions[this.viewBy], this.commentsForRubric);
      return R.values(convertedReviews);
    }
  },
  methods: {
    emitTitles() {
      this.$emit('title-resolved', this.promptTitle);
      this.$emit('subtitle-resolved', 'Reviews Received');
    },
    fetchReviewsReceived() {
      const {courseId, studentId, rubricId} = this;
      const payload = {
        api: this.$api,
        courseId,
        studentId,
        rubricId
      };
      return this.$store.dispatch('fetchCommentsForRubric', payload);
    }
  },
  mounted() {
    this.fetchReviewsReceived()
      .then(this.emitTitles);
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

    .control-button:hover {
        cursor: pointer;
    }

    .control-button--active {
        background-color: white;
        color: black;
    }

    .control-button:focus {
        outline: 0;
    }
</style>
