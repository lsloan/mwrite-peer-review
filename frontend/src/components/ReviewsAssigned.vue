<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">
                <h1>Assigned to me</h1>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>
        <div class="mdl-grid" v-if="prompts.length === 0">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">
                <p>You have no reviews to complete at this time.</p>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>
        <div class="mdl-grid" v-else v-for="prompt in prompts" :key="prompt.id">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <div
                class="assigned-review-card mdl-card mdl-shadow--2dp mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">
                <div class="assigned-review-header">
                    <span>{{ prompt.promptName }}</span>
                    <div class="due-date-container">
                        <i class="material-icons">query_builder</i>
                        <span>Due</span>
                        <span v-if="prompt.dueDateUtc">{{ prompt.dueDateUtc | utcToLocal('MMMM D h:mm A') }}</span>
                        <span v-else>anytime</span>
                    </div>
                </div>
                <div class="reviews-container mdl-grid">
                    <div v-for="(review, index) in prompt.reviews" :key="review.reviewId"
                         class="submission-for-review mdl-cell mdl-cell--4-col">
                        <div class="student-name-container">Student {{ index + 1 }}</div>
                        <div class="review-status-container">
                            <div v-if="review.reviewIsComplete" class="review-complete-container">
                                <i class="material-icons evaluation-complete-icon">done</i>
                                <span>Submitted</span>
                            </div>
                            <router-link
                                v-else
                                :to="{name: 'PeerReview', params: {reviewId: review.reviewId}}"
                                class="start-review-button mdl-button mdl-js-button start-review-button mdl-button--colored">
                                Start Review
                            </router-link>
                        </div>
                    </div>
                </div>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>
    </div>
</template>

<script>
import DateFormat from '@/mixins/date-format';

export default {
  name: 'ReviewsAssigned',
  props: ['prompts'],
  mixins: [DateFormat],
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    }
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
        background-color: #3f51b5;
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
        width: 100%;
        box-sizing: border-box;
    }

    .mdl-grid > .submission-for-review {
        background-color: white;
        font-size: 14px;
        box-shadow: 0 2px 2px 0 rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.2), 0 1px 5px 0 rgba(0,0,0,.12);
    }

    .student-name-container {
        border-bottom: 1px solid lightgray;
        font-weight: bold;
        padding: 14px 8px;
    }

    .review-status-container {
        text-transform: uppercase;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .start-review-button {
        padding: 0;
        height: 38px;
        width: 100%;
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
