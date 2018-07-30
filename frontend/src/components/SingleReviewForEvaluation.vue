<template>
    <review-by-reviewer class="review" :review="review" :always-show-evaluation="true"/>
</template>

<script>
import {conversions} from '@/services/reviews';
import ReviewByReviewer from '@/components/ReviewByReviewer';

export default {
  name: 'SingleReviewForEvaluation',
  props: ['student-id', 'peer-review-id'],
  components: {ReviewByReviewer},
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    comments() {
      const reviewId = parseInt(this.peerReviewId);
      return this.$store.getters.commentsBy.peerReview[reviewId];
    },
    review() {
      return this.comments
        ? [this.comments].map(conversions.reviewer)[0]
        : [];
    },
    promptTitle() {
      return this.comments && this.comments.length > 0
        ? this.comments[0].promptTitle
        : '';
    }
  },
  methods: {
    fetchReview() {
      const {courseId, studentId, peerReviewId} = this;
      return this.$store.dispatch('fetchCommentsForReview', {
        api: this.$api,
        courseId,
        studentId,
        peerReviewId
      });
    },
    emitTitle() {
      this.$emit('title-resolved', this.promptTitle);
    }
  },
  mounted() {
    this.fetchReview()
      .then(this.emitTitle);
  }
};
</script>

<style scoped>
    .review {
        margin: 15px 20px;
    }
</style>
