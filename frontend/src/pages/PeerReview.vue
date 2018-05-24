<template>
    <div>
        <peer-review-section section-number="1">
            <a :href="submissionDownloadUrl"
                class="mdl-button mdl-button--raised mdl-button--colored mdl-js-button mdl-js-ripple-effect">
                Download Submission
            </a>
        </peer-review-section>
    </div>
</template>

<script>
import PeerReviewSection from '@/components/PeerReviewSection';

export default {
  name: 'PeerReview',
  props: ['review-id'],
  components: {PeerReviewSection},
  computed: {
    submissionDownloadUrl() {
      const {courseId} = this.$store.state.userDetails;
      return __API_URL__ + '/course/' + courseId + '/reviews/' + this.reviewId + '/submission';
    }
  }
};
</script>

<style scoped>
    h1 {
        font-size: 24px;
        line-height: 24px;
        margin: 8px 0;
    }
</style>
