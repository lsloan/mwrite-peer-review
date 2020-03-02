<template>
    <div>
        <completed-work :reviews="completedReviews"/>
        <assigned-work :prompts="prompts" :evaluations="mandatoryEvaluations"/>
        <router-view/>
    </div>
</template>

<script>
import * as R from 'ramda';

import { MdlCard, MdlAnchorButton } from 'vue-mdl';

import AssignedWork from '@/components/AssignedWork';
import CompletedWork from '@/components/CompletedWork';

const makeEvaluationEntry = ([rubricId, evaluations]) => ({
  peerReviewTitle: evaluations[0].peerReviewTitle,
  dueDateUtc: evaluations[0].dueDateUtc,
  evaluations: evaluations
});

export default {
  name: 'student-dashboard',
  components: {
    MdlCard,
    MdlAnchorButton,
    AssignedWork,
    CompletedWork
  },
  data() {
    return {
      prompts: [],
      completedReviews: []
    };
  },
  computed: {
    mandatoryEvaluations() {
      // TODO consider moving some of this logic to Vuex getter(s)
      return R.pipe(
        R.filter(e => e.evaluationIsMandatory),
        R.groupBy(e => e.rubricId),
        R.map(evals => R.sortBy(e => e.studentId, evals)),
        R.toPairs,
        R.map(makeEvaluationEntry),
        R.filter(entry => !R.all(e => e.evaluationIsComplete, entry.evaluations))
      )(this.$store.state.pendingEvaluations);
    }
  },
  methods: {
    setPromptsForReview(data) {
      this.prompts = data;
    },
    setCompletedReviews(data) {
      this.completedReviews = data;
    }
  },
  mounted() {
    // TODO combine promises?
    const {courseId, userId} = this.$store.state.userDetails;
    this.$api.get('/course/{}/reviews/student/{}/assigned', courseId, userId)
      .then(response => this.setPromptsForReview(response.data));
    this.$api.get('/course/{}/reviews/student/{}/completed', courseId, userId)
      .then(response => this.setCompletedReviews(response.data));
    this.$store.dispatch('fetchPendingEvaluations', {
      api: this.$api,
      courseId,
      userId
    });
  }
};
</script>

<style scoped>
</style>
