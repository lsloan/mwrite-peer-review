<template>
    <reviews-by-criterion class="reviews" :data="entries"/>
</template>

<script>
import {denormalizers} from '@/services/reviews';
import ReviewsByCriterion from '@/components/ReviewsByCriterion';

export default {
  name: 'SingleReview',
  props: ['review-id'],
  components: {ReviewsByCriterion},
  data() {
    return {
      data: {}
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    entries() {
      const {entries = []} = this.data;
      return denormalizers['criterion'](entries);
    },
    title() {
      const {promptTitle = ''} = this.data;
      return promptTitle;
    }
  },
  mounted() {
    this.$api.get('/course/{}/reviews/{}', this.courseId, this.reviewId)
      .then(r => {
        this.data = r.data;
        this.$emit('title-resolved', this.title);
      });
  }
};
</script>

<style scoped>
    .reviews {
        margin: 15px;
    }
</style>
