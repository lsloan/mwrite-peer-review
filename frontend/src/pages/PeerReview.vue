<template>
    <div>
        <peer-review-section section-number="1">
            <mdl-anchor-button :href="submissionDownloadUrl" colored raised>
                Download Submission
            </mdl-anchor-button>
        </peer-review-section>
        <peer-review-section section-number="2">
            <h1>Submit Your Review</h1>
        </peer-review-section>
        <peer-review-section>
            <p class="preserve-whitespace">{{ rubricDescription }}</p>
        </peer-review-section>
        <form @submit.prevent>
            <peer-review-section v-for="criterion in criteria" :key="criterion.id">
                <p class="preserve-whitespace" >{{ criterion.description }}</p>
                <autosize-textarea
                    class="criterion-input"
                    label="Your comment goes here..."
                    v-model="responses[criterion.id]"/>
            </peer-review-section>
            <peer-review-section>
                <mdl-button raised colored @click.native="submitReview" :disabled="!reviewIsComplete">
                    Submit
                </mdl-button>
                <mdl-button @click.native="cancelReview">
                    Cancel
                </mdl-button>
            </peer-review-section>
        </form>
        <mdl-snackbar display-on="notification"/>
    </div>
</template>

<script>
import * as R from 'ramda';
import {MdlButton, MdlAnchorButton} from 'vue-mdl';

import api from '@/services/api';
import PeerReviewSection from '@/components/PeerReviewSection';
import AutosizeTextarea from '@/components/AutosizeTextarea';

const NOTIFICATION_TIMEOUT_MS = 5000;

export default {
  name: 'PeerReview',
  props: ['review-id'],
  components: {PeerReviewSection, AutosizeTextarea, MdlButton, MdlAnchorButton},
  data() {
    return {
      data: {},
      responses: {}
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    rubricDescription() {
      return this.data.description || '';
    },
    criteria() {
      const {criteria = []} = this.data;
      return R.sortBy(c => c.id, criteria);
    },
    comments() {
      return R.toPairs(this.responses)
        .filter(([_, comment]) => R.trim(comment))
        .map(([criterionId, comment]) => ({
          criterionId: parseInt(criterionId),
          comment: R.trim(comment)
        }));
    },
    reviewIsComplete() {
      return this.criteria.length === this.comments.length;
    },
    submissionDownloadUrl() {
      return `${__API_URL__}/course/${this.courseId}/reviews/${this.reviewId}/submission`;
    }
  },
  methods: {
    submitReview() {
      if(this.reviewIsComplete) {
        const data = {comments: this.comments};
        api.post('/course/{}/reviews/{}/', data, this.courseId, this.reviewId)
          .then(() => {
            this.$root.$emit('notification', {
              message: 'Thank you for submitting your peer review!  You will be returned to the dashboard.',
              timeout: NOTIFICATION_TIMEOUT_MS - 500
            });
            setTimeout(() => this.$router.push('/student/dashboard'), NOTIFICATION_TIMEOUT_MS);
          })
          .catch(() => {
            this.$root.$emit('notification', {
              message: 'An error occurred.  Please try again later.',
              timeout: NOTIFICATION_TIMEOUT_MS
            });
          });
      }
      else {
        this.$root.$emit('notification', {
          message: 'Your review is not complete.  Double check that you have entered a response for all criteria.',
          timeout: NOTIFICATION_TIMEOUT_MS
        });
      }
    },
    cancelReview() {
      this.$router.back();
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
    h1, p {
        font-family: "Roboto","Helvetica","Arial",sans-serif;
    }

    h1 {
        font-size: 24px;
        line-height: 24px;
        margin: 8px 0;
    }

    p {
        font-size: 16px;
    }

    .criterion-input {
        width: 100%;
    }

    .preserve-whitespace {
        white-space: pre;
    }
</style>
