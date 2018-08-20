<template>
    <div>
        <div v-for="subEntry in review.entries" :key="subEntry.id">
            <p class="heading">{{ subEntry.heading }}</p>
            <p>{{ subEntry.content }}</p>
        </div>
        <review-evaluation v-if="allowEvaluation" :evaluation="evaluation" :always-show="alwaysShowEvaluation"/>
    </div>
</template>

<script>
import ReviewEvaluation from '@/components/ReviewEvaluation';

export default {
  name: 'ReviewByReviewer',
  props: ['review', 'allow-evaluation', 'always-show-evaluation'],
  components: {ReviewEvaluation},
  computed: {
    evaluation() {
      const {peerReviewId} = this.review;
      return this.$store.state.pendingEvaluations.find(e => e.peerReviewId === peerReviewId);
    }
  }
};
</script>

<style scoped>
    .heading {
        font-weight: bold;
        margin-bottom: 0;
    }
</style>
