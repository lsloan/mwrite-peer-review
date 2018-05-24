<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col">
                <aside class="section-number-container">
                    <p class="section-number">1</p>
                </aside>
            </div>
            <div class="mdl-cell mdl-cell--10-col">
                <a :href="submissionDownloadUrl"
                   class="mdl-button mdl-button--raised mdl-button--colored mdl-js-button mdl-js-ripple-effect">
                   Download Submission
                </a>
            </div>
            <div class="mdl-cell mdl-cell--1-col"></div>
        </div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col">
                <aside class="section-number-container">
                    <p class="section-number">2</p>
                </aside>
            </div>
            <div class="mdl-cell mdl-cell--10-col">
                <h1>Submit Your Review</h1>
            </div>
            <div class="mdl-cell mdl-cell--1-col"></div>
        </div>
    </div>
</template>

<script>
export default {
  name: 'PeerReview',
  props: ['review-id'],
  computed: {
    submissionDownloadUrl() {
      const {courseId} = this.$store.state.userDetails;
      return __API_URL__ + '/course/' + courseId + '/reviews/' + this.reviewId + '/submission';
    }
  }
};
</script>

<style scoped>
    .section-number-container {
        display: flex;
        flex-direction: row-reverse;
    }

    .section-number {
        text-align: center;
        color: white;
        background: #4187CD;
        width: 36px;
        height: 36px;
        line-height: 36px;
        -moz-border-radius: 18px;
        -webkit-border-radius: 18px;
        border-radius: 18px;
    }

    h1 {
        font-size: 24px;
        line-height: 24px;
        margin: 8px 0;
    }
</style>
