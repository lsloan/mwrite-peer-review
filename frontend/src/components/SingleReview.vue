<template>
    <reviews-by-criterion class="reviews" :data="entries"/>
</template>

<script>
import {conversions} from '@/services/reviews';
import ReviewsByCriterion from '@/components/ReviewsByCriterion';

export default {
  name: 'SingleReview',
  props: ['review-id'],
  components: {ReviewsByCriterion},
  data() {
    return {
      review: []
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    entries() {
      return this.review.map(conversions.criterion);
    },
    promptTitle() {
      return this.review[0][0].promptTitle;
    }
  },
  mounted() {
    this.$api.get('/course/{}/reviews/{}', this.courseId, this.reviewId)
      .then(r => {
        this.review = [r.data];
        this.$emit('title-resolved', this.promptTitle);
      });
  }
};
</script>

<style scoped>
    .reviews {
        margin: 15px;
    }
</style>
