<template>
    <div>
        <assigned-work :prompts="prompts" :evaluations="mandatoryEvaluations"/>
        <reviews-completed :reviews="completedReviews"/>
        <router-view/>
    </div>
</template>

<script>
import * as R from 'ramda';

import { MdlCard, MdlAnchorButton } from 'vue-mdl';

import AssignedWork from '@/components/AssignedWork';
import ReviewsCompleted from '@/components/ReviewsCompleted';

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
    ReviewsCompleted
  },
  data() {
    return {
      prompts: [],
      completedReviews: []
    };
  },
  computed: {
    mandatoryEvaluations() {
      // TODO filter out non-mandatory evaluations
      // TODO filter out rubric / eval entry if all evals are complete
      return R.pipe(
        R.groupBy(e => e.rubricId),
        R.map(evals => R.sortBy(e => e.studentId, evals)),
        R.toPairs,
        R.map(makeEvaluationEntry)
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
