<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--2-col-phone">
                <h1>Assigned to me</h1>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
        </div>
        <div class="mdl-grid" v-if="promptsForReview.length === 0">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--2-col-phone">
                <p>You have no reviews to complete at this time.</p>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
        </div>
        <div class="mdl-grid" v-else v-for="prompt in promptsForReview" :key="prompt.id">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--1-col-phone"></div>
            <div class="assigned-review-card mdl-card mdl-shadow--2dp mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--2-col-phone">
                <div class="assigned-review-header">
                    <span>{{ prompt.promptName }}</span>
                    <div class="due-date-container">
                        <i class="material-icons">query_builder</i>
                        <span>Due</span>
                        <span v-if="prompt.dueDateUtc">{{ prompt.dueDateUtc | utcToLocal('MMMM D h:mm A') }}</span>
                        <span v-else>anytime</span>
                    </div>
                </div>
                <div class="reviews-container">
                    <div v-for="review in prompt.reviews" :key="review.reviewId" class="submission-container">
                        <div class="submission-for-review">
                            <div class="student-name-container">Student {{ review.reviewId }}</div>
                            <div class="review-status-container">
                                <div v-if="review.reviewIsComplete" class="review-complete-container">
                                    <i class="material-icons evaluation-complete-icon">done</i>
                                    <span>Submitted</span>
                                </div>
                                <div v-else class="review-start-container">
                                    <!-- TODO replace with <router-link/> once review submission page is ported to Vue-->
                                    <!-- TODO use peer review ID instead of submission ID? -->
                                    <mdl-anchor-button colored :href="apiUrl + '/course/'+ courseId + '/review/submission/' + review.submissionId">
                                        Start Review
                                    </mdl-anchor-button>
                                </div>
                            </div>
                        </div>
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
import { MdlCard, MdlAnchorButton } from 'vue-mdl';
import DateFormat from '@/mixins/date-format';

export default {
  name: 'student-dashboard',
  components: {
    MdlCard,
    MdlAnchorButton
  },
  mixins: [DateFormat],
  data() {
    return {
      apiUrl: __API_URL__, // TODO remove this when review submission page is ported to VueJS
      promptsForReview: []
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    studentId() {
      return this.$store.state.userDetails.userId;
    }
  },
  mounted() {
    this.$api.get('/course/{}/reviews/student/{}/assigned', this.courseId, this.studentId)
      .then(response => {
        this.promptsForReview = response.data;
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
        min-height: initial;
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

    .reviews-container {
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .submission-container {
        flex-grow: 1;
        flex-shrink: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px 25px;
    }

    .submission-for-review {
        display: inline-block;
        width: 100%;
        background-color: white;
        font-size: 14px;
        box-shadow: 0 2px 2px 0 rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.2), 0 1px 5px 0 rgba(0,0,0,.12);
    }

    .student-name-container {
        border-bottom: 1px solid lightgray;
        font-weight: bold;
        padding: 8px;
    }

    .review-status-container {
        text-transform: uppercase;
        padding: 0 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .review-start-container > a.mdl-button {
        padding: 0;
        height: 38px;
    }

    .review-complete-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        text-transform: uppercase;
        color: #52A763;
        padding: 9px 0;
    }

    .review-complete-container > i.material-icons {
        font-size: 16px;
        margin-right: 4px;
    }
</style>
