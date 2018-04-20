<template>
    <div>
        <reviews-assigned :prompts="prompts"/>
        <reviews-completed :reviews="completedReviews"/>

        <div class="mdl-grid">
            <!-- TODO "completed work" section goes here -->
        </div>
        <router-link :to="{name: 'ReviewsGiven', params: {studentId: studentId, rubricId: 1}}">
            open sample reviews given modal
        </router-link>
        <router-link :to="{name: 'ReviewsReceived', params: {studentId: studentId, rubricId: 1}}">
            open sample reviews received modal
        </router-link>
        <router-view/>
    </div>
</template>

<script>
import { sortBy } from 'ramda';
import moment from 'moment';
import { MdlCard, MdlAnchorButton } from 'vue-mdl';
import ReviewsAssigned from '@/components/ReviewsAssigned';
import ReviewsCompleted from '@/components/ReviewsCompleted';

const byDateAscending = (a, b) => {
  const dateA = moment.utc(a.dueDateUtc);
  const dateB = moment.utc(b.dueDateUtc);
  return dateA.diff(dateB);
};

const sortReviews = prompt => {
  const sortedReviews = sortBy(r => r.reviewId, prompt.reviews);
  return Object.assign({}, prompt, {reviews: sortedReviews});
};

export default {
  name: 'student-dashboard',
  components: {
    MdlCard,
    MdlAnchorButton,
    ReviewsAssigned,
    ReviewsCompleted
  },
  data() {
    return {
      prompts: [],
      completedReviews: []
    };
  },
  methods: {
    setPromptsForReview(data) {
      this.prompts = data.map(sortReviews).sort(byDateAscending);
    },
    setCompletedReviews(data) {
      this.completedReviews = data.sort(byDateAscending);
    }
  },
  computed: {
    studentId() {
      return this.$store.state.userDetails.userId; // TODO remove after implementing completed work section?
    }
  },
  mounted() {
    const {courseId, userId} = this.$store.state.userDetails;
    this.$api.get('/course/{}/reviews/student/{}/assigned', courseId, userId)
      .then(response => this.setPromptsForReview(response.data));
    this.$api.get('/course/{}/reviews/student/{}/completed', courseId, userId)
      .then(response => this.setCompletedReviews(response.data));
  }
};
</script>

<style scoped>
</style>
