<template>
    <div class="evaluation-container">
        <div v-if="evaluationIsComplete" class="evaluation-complete">
            <i class="material-icons evaluation-complete-icon">done</i>
            <span>Submitted</span>
        </div>
        <div v-else>
            <div v-if="!alwaysShow && !showEvaluation">
                <button class="evaluation-button" @click="showEvaluation = true">Rate This Evaluation</button>
            </div>
            <form v-else class="evaluation-card" v-on:submit.prevent>
                <div class="form-section">
                    <fieldset class="usefulness-fields">
                        <legend class="form-label">Please rate the overall usefulness of this review</legend>
                        <div class="radio-controls">
                            <div class="radio-control">
                                <input id="usefulness-choice-1" type="radio" v-model="usefulness" value="1"/>
                                <label for="usefulness-choice-1">Very unuseful</label>
                            </div>
                            <div class="radio-control">
                                <input id="usefulness-choice-2" type="radio" v-model="usefulness" value="2"/>
                                <label for="usefulness-choice-2">Unuseful</label>
                            </div>
                            <div class="radio-control">
                                <input id="usefulness-choice-3" type="radio" v-model="usefulness" value="3"/>
                                <label for="usefulness-choice-3">Somewhat useful</label>
                            </div>
                            <div class="radio-control">
                                <input id="usefulness-choice-4" type="radio" v-model="usefulness" value="4"/>
                                <label for="usefulness-choice-4">Useful</label>
                            </div>
                            <div class="radio-control">
                                <input id="usefulness-choice-5" type="radio" v-model="usefulness" value="5"/>
                                <label for="usefulness-choice-5">Very useful</label>
                            </div>
                        </div>
                    </fieldset>
                </div>
                <div class="form-section">
                    <label>
                        <span class="form-label">Please provide any additional feedback on this review</span>
                        <mdl-textfield
                            class="feedback-input"
                            v-model="comment"/>
                    </label>
                </div>
                <div class="form-section">
                    <mdl-button
                        colored
                        raised
                        :disabled="!usefulness"
                        @click.native="submitEvaluation()">
                        Submit
                    </mdl-button>
                    <mdl-button
                        v-if="!alwaysShow"
                        colored
                        @click.native="showEvaluation = false">
                        Cancel
                    </mdl-button>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import { MdlButton } from 'vue-mdl';

export default {
  name: 'ReviewEvaluation',
  props: ['evaluation', 'always-show'],
  components: {
    MdlButton
  },
  data() {
    return {
      showEvaluation: this.alwaysShow,
      usefulness: null,
      comment: null
    };
  },
  computed: {
    evaluationIsComplete() {
      const {evaluation: {evaluationIsComplete = false} = {}} = this;
      return evaluationIsComplete;
    }
  },
  methods: {
    markAsComplete() {
      const {peerReviewId} = this.evaluation;
      this.$store.commit('markEvaluationCompleteForReview', peerReviewId);
    },
    submitEvaluation() {
      const {courseId, userId} = this.$store.state.userDetails;
      const {usefulness, comment, evaluation: {peerReviewId}} = this;
      const data = {usefulness, comment};
      const payload = {
        api: this.$api,
        courseId,
        userId,
        peerReviewId,
        data
      };
      this.$store.dispatch('submitEvaluation', payload)
        .then(this.markAsComplete);
    }
  }
};
</script>

<style scoped>
    .evaluation-container {
        margin-top: 35px;
    }

    .evaluation-complete {
        display: flex;
        flex-direction: row;
        align-items: center;
        text-transform: uppercase;
        color: #2F8540;
    }

    .evaluation-complete-icon {
        margin-right: 8px;
    }

    .evaluation-card {
        border: 1px solid lightgray;
        border-top: 4px solid #4157AF;
        padding: 8px 20px;
    }

    .form-section {
        margin-bottom: 15px;
    }

    .form-label {
        font-weight: bolder;
        display: block;
        margin-bottom: 8px;
    }

    .usefulness-fields {
        margin: 0 10px;
    }

    .usefulness-fields > legend {
        margin: 0 -10px 8px -10px;
    }

    .feedback-input {
        width: 100%;
        padding: 0;
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

    .radio-controls {
        display: flex;
        flex-direction: row;
    }

    .radio-control {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 13px;
        text-align: center;
    }
</style>
