<template>
    <div>
        <assigned-work :prompts="prompts" :evaluations="evaluations"/>
        <reviews-completed :reviews="completedReviews"/>
        <router-view/>
    </div>
</template>

<script>
import { MdlCard, MdlAnchorButton } from 'vue-mdl';

import AssignedWork from '@/components/AssignedWork';
import ReviewsCompleted from '@/components/ReviewsCompleted';

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
      evaluations: [],
      completedReviews: []
    };
  },
  methods: {
    setPromptsForReview(data) {
      this.prompts = data;
    },
    setCompletedReviews(data) {
      this.completedReviews = data;
    },
    setEvaluations(data) {
      this.evaluations = data;
    }
  },
  mounted() {
    // TODO combine promises?
    const {courseId, userId} = this.$store.state.userDetails;
    this.$api.get('/course/{}/reviews/student/{}/assigned', courseId, userId)
      .then(response => this.setPromptsForReview(response.data));
    this.$api.get('/course/{}/reviews/student/{}/completed', courseId, userId)
      .then(response => this.setCompletedReviews(response.data));
    this.$api.get('/course/{}/reviews/student/{}/evaluation/pending', courseId, userId)
      .then(response => this.setEvaluations(response.data));
  }
};
</script>

<style scoped>
</style>
