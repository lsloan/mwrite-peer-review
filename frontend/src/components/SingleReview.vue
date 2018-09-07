<template>
    <reviews-by-criterion class="reviews" :data="review" :evaluation="evaluation" />
</template>

<script>
import {conversions} from '@/services/reviews';
import ReviewsByCriterion from '@/components/ReviewsByCriterion';
import {navigateToErrorPage} from '@/router/helpers';
import api from '@/services/api';

export default {
  name: 'SingleReview',
  props: ['review-id'],
  components: {ReviewsByCriterion},
  data() {
    return {
      evaluation: null
    };
  },
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
    fetchEvaluation() {
      api.get('/course/{}/reviews/{}/evaluation', this.courseId, this.reviewId)
        .then(response => {
          this.evaluation = response.data;
        })
        .catch(reason => {
          if(reason.response.status !== 404) {
            navigateToErrorPage(this, null, reason);
          }
        });
    },
    emitTitle() {
      this.$emit('title-resolved', this.promptTitle);
    }
  },
  mounted() {
    this.fetchReview()
      .then(this.emitTitle);
    this.fetchEvaluation();
  }
};
</script>

<style scoped>
    .reviews {
        margin: 15px;
    }
</style>
