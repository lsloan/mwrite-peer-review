<template>
    <div>
        <peer-review-section section-number="1">
            <a :href="submissionDownloadUrl"
                class="mdl-button mdl-button--raised mdl-button--colored mdl-js-button mdl-js-ripple-effect">
                Download Submission
            </a>
        </peer-review-section>
        <peer-review-section section-number="2">
            <h1>Submit Your Review</h1>
        </peer-review-section>
        <peer-review-section>
            <p>{{ rubricDescription }}</p>
        </peer-review-section>
        <peer-review-section v-for="criterion in criteria" :key="criterion.id">
            <p>{{ criterion.description }}</p>
            <autosize-textarea
                class="criterion-input"
                label="Your comment goes here..."
                v-model="responses[criterion.id]"/>
        </peer-review-section>
    </div>
</template>

<script>
import * as R from 'ramda';

import PeerReviewSection from '@/components/PeerReviewSection';
import AutosizeTextarea from '@/components/AutosizeTextarea';

export default {
  name: 'PeerReview',
  props: ['review-id'],
  data() {
    return {
      data: {},
      responses: {}
    };
  },
  components: {PeerReviewSection, AutosizeTextarea},
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    rubricDescription() {
      return this.data.description;
    },
    criteria() {
      return R.sortBy(R.prop('id'), this.data.criteria);
    },
    submissionDownloadUrl() {
      return __API_URL__ + '/course/' + this.courseId + '/reviews/' + this.reviewId + '/submission';
    }
  },
  mounted() {
    this.$api.get('/course/{}/reviews/{}/rubric', this.courseId, this.reviewId).then(r => {
      this.data = r.data;
    });
  }
};
</script>

<style scoped>
    h1 {
        font-size: 24px;
        line-height: 24px;
        margin: 8px 0;
    }

    h1, p {
        font-family: "Roboto","Helvetica","Arial",sans-serif;
    }

    .criterion-input {
        width: 100%;
    }
</style>
