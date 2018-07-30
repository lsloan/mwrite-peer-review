<template>
    <reviews-by-criterion class="reviews" :data="review"/>
</template>

<script>
import {conversions} from '@/services/reviews';
import ReviewsByCriterion from '@/components/ReviewsByCriterion';

export default {
  name: 'SingleReview',
  props: ['review-id'],
  components: {ReviewsByCriterion},
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    comments() {
      const reviewId = parseInt(this.reviewId);
      return this.$store.getters.commentsBy.peerReview[reviewId];
    },
    review() {
      return this.comments
        ? [this.comments].map(conversions.criterion)
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
      return this.$store.dispatch('fetchCommentsForReview', {
        courseId: this.courseId,
        peerReviewId: this.reviewId,
        api: this.$api
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
    .reviews {
        margin: 15px;
    }
</style>
