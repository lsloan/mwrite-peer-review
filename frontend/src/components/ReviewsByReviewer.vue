<template>
    <div>
        <mdl-tabs v-model="selectedTab" class="tabs">
            <mdl-tab v-for="entry in data" :key="entry.id" :tab="entry.title">
                <div v-for="subEntry in entry.entries" :key="subEntry.id">
                    <p class="heading">{{ subEntry.heading }}</p>
                    <p>{{ subEntry.content }}</p>
                </div>
            </mdl-tab>
        </mdl-tabs>

        <div v-if="!showEvaluation">
            <div v-if="!selectedEvaluationSubmitted">
                <button @click="showEvaluation = true">Rate This Evaluation</button>
            </div>
            <div v-else>
                <p>Submitted</p>
            </div>
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
            <button @click="submitEvaluation">Submit</button>
            <button @click="showEvaluation = false">Cancel</button>
        </div>

    </div>
</template>

<script>
import {MdlTab, MdlTabs, MdlRadio} from 'vue-mdl';

export default {
  name: 'reviews-by-reviewer',
  props: ['data'],
  components: {MdlTab, MdlTabs, MdlRadio},
  data() {
    return {
      selectedTab: '',
      showEvaluation: false,
      usefulness: null,
      evaluationComment: null
    };
  },
  computed: {
    selectedPeerReviewId() {
      if(this.data) {
        const entry = this.data.find(e => e.title === this.selectedTab);
        return entry.peerReviewId;
      }
    },
    selectedEvaluationSubmitted() {
      if(this.data) {
        const entry = this.data.find(e => e.title === this.selectedTab);
        return entry.evaluationSubmitted;
      }
    }
  },
  methods: {
    submitEvaluation() {
      console.log(
        'would have submitted',
        this.usefulness,
        'and',
        this.evaluationComment,
        'for', this.selectedPeerReviewId
      );
    }
  },
  watch: {
    data() {
      if(this.data.length > 0) {
        this.selectedTab = this.data[0].title;
      }
    }
  }
};
</script>

<style scoped>
    .heading {
        font-weight: bold;
        margin-bottom: 0;
    }

    .tabs >>> .mdl-tabs__tab-bar {
        border: initial;
        justify-content: initial;
        -webkit-justify-content: initial;
        padding-bottom: 25px;
    }
</style>
