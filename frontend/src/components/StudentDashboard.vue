<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--2-col-phone">
                <h1>Assigned to me</h1>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
        </div>
        <div class="mdl-grid" v-if="assignedReviews.length === 0">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--2-col-phone">
                <p>You have no reviews to complete at this time.</p>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
        </div>
        <div class="mdl-grid" v-else v-for="(review, i) in assignedReviews" :key="i">  <!-- TODO use real prompt IDs for :key -->
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
            <div class="assigned-review-card mdl-card mdl-shadow--2dp mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--2-col-phone">
                <div class="assigned-review-header">
                    <span>{{ review.promptName }}</span>
                    <div class="due-date-container">
                        <i class="material-icons">query_builder</i>
                        <span>Due</span>
                        <span v-if="review.dueDateUtc">{{ review.dueDateUtc | utcToLocal('MMMM D h:mm A') }}</span>
                        <span v-else>anytime</span>
                    </div>
                </div>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
        </div>
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
import { MdlCard } from 'vue-mdl';
import DateFormat from '@/mixins/date-format';

export default {
  name: 'student-dashboard',
  components: {
    MdlCard
  },
  mixins: [DateFormat],
  data() {
    return {
      assignedReviews: []
    };
  },
  computed: {
    studentId() {
      return this.$store.state.userDetails.userId;
    }
  },
  mounted() {
    const {courseId, userId} = this.$store.state.userDetails;
    this.$api.get('/course/{}/reviews/student/{}/assigned', courseId, userId)
      .then(response => {
        this.assignedReviews = response.data;
      });
  }
};
</script>

<style scoped>
    h1 {
        font-size: 24px;
        margin: 4px 0;
        font-weight: bolder;
    }

    .assigned-review-card {
        background-color: #F0F0F0;
    }

    .assigned-review-header {
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 0 20px;
        background-color: #4183C9;
        color: white;
        flex: 0 0 64px;
    }

    .due-date-container {
        margin-left: auto;
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .due-date-container > span, .due-date-container > .material-icons {
        margin-right: 6px;
    }
</style>
