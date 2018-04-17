<template>
    <div class="evaluation-container">
        <div v-if="evaluationSubmitted">
            <p>Submitted</p>
        </div>
        <div v-else>
            <div v-if="!showEvaluation">
                <button class="evaluation-button" @click="showEvaluation = true">Rate This Evaluation</button>
            </div>
            <div v-else>
                <label>
                    Please rate the overall usefulness of this review
                    <mdl-radio v-model="usefulness" val="1">Very unuseful</mdl-radio>
                    <mdl-radio v-model="usefulness" val="2">Unuseful</mdl-radio>
                    <mdl-radio v-model="usefulness" val="3">Somewhat useful</mdl-radio>
                    <mdl-radio v-model="usefulness" val="4">Useful</mdl-radio>
                    <mdl-radio v-model="usefulness" val="5">Very useful</mdl-radio>
                </label>
                <mdl-textfield
                    v-model="evaluationComment"
                    label="Please provide any additional feedback on this review"/>
                <button @click="submitEvaluation(entry)">Submit</button>
                <button @click="showEvaluation = false">Cancel</button>
            </div>
        </div>
    </div>
</template>

<script>
import {MdlRadio} from 'vue-mdl';

export default {
  name: 'ReviewEvaluation',
  props: ['entry'],
  components: {MdlRadio},
  data() {
    return {
      showEvaluation: false,
      usefulness: null,
      evaluationComment: null,
      userSubmittedEvaluation: false
    };
  },
  computed: {
    evaluationSubmitted() {
      return this.userSubmittedEvaluation || this.entry.evaluationSubmitted;
    }
  },
  methods: {
    submitEvaluation(entry) {
      const {courseId, userId} = this.$store.state.userDetails;
      const data = {
        usefulness: this.usefulness,
        comment: this.evaluationComment
      };
      this.$api.post('/course/{}/reviews/student/{}/evaluation/{}', data, courseId, userId, entry.peerReviewId)
        .then(() => {
          this.userSubmittedEvaluation = true;
          this.showEvaluation = false;
        });
    }
  }
};
</script>

<style scoped>
    .evaluation-container {
        margin-top: 35px;
    }

    .evaluation-button {
        border: 1px solid #4157AF;
        background-color: white;
        color: #4157AF;
        padding: 10px 18px 11px 18px;
        text-transform: uppercase;
        font-size: 14px;
    }

    .evaluation-button:focus {
        outline: 0;
    }
</style>
