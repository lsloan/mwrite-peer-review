<template>
    <div class="mdl-card mdl-cell mdl-cell--3-col mdl-shadow--2dp">
        <div :class="titleBarClasses">
            {{ rubric.title }}
        </div>
        <div class="mdl-card__supporting-text">
            <div class="status-line">
                <i class="material-icons">
                    <template v-if="rubric.reviewInfo.submissionPresent">
                        attachment
                    </template>
                    <template v-else-if="!rubric.reviewsWereDistributed">
                        more_horiz
                    </template>
                    <template v-else>warning</template>
                </i>
                <span>
                    Prompt
                    <template v-if="!rubric.reviewInfo.submissionPresent">not</template>
                    submitted
                    <template v-if="!rubric.reviewInfo.submissionPresent && !rubric.reviewsWereDistributed">
                        yet
                    </template>
                </span>
            </div>
        </div>
        <div class="mdl-card__supporting-text">
            <div class="status-line">
                <template v-if="!rubric.reviewsWereDistributed">
                    <i class="material-icons">more_horiz</i>
                    <span>Reviews not assigned yet</span>
                </template>
                <template v-else-if="!rubric.reviewInfo.submissionPresent">
                    <i class="material-icons">warning</i>
                    <span>Prompt not submitted</span>
                </template>
                <template v-else>
                    <i class="material-icons">
                        <template v-if="noReviewsCompleted">warning</template>
                        <template v-else-if="!allReviewsCompleted || someCompletedLate">error_outline</template>
                        <template v-else>done</template>
                    </i>
                    <span>
                        Submitted
                        {{ rubric.reviewInfo.completed }}/{{ rubric.reviewInfo.totalToComplete }}
                        peer reviews
                        <template v-if="someCompletedLate">
                            ({{ rubric.reviewInfo.completedLate }} late)
                        </template>
                    </span>
                </template>
            </div>
        </div>
        <div class="mdl-card__supporting-text">
            <div class="status-line">
                <template v-if="!rubric.reviewsWereDistributed">
                    <i class="material-icons">more_horiz</i>
                    <span>Reviews not assigned yet</span>
                </template>
                <template v-else-if="!rubric.reviewInfo.submissionPresent">
                    <i class="material-icons">warning</i>
                    <span>Prompt not submitted</span>
                </template>
                <template v-else>
                    <i class="material-icons">
                        <template v-if="noReviewsReceived">warning</template>
                        <template v-else-if="!allReviewsReceived || someReceivedLate">error_outline</template>
                        <template v-else>done</template>
                    </i>
                    <span>
                        Received
                        {{ rubric.reviewInfo.received }}/{{ rubric.reviewInfo.totalToReceive }}
                        peer reviews
                        <template v-if="someReceivedLate">
                            ({{ rubric.reviewInfo.receivedLate }} late)
                        </template>
                    </span>
                </template>
            </div>
        </div>
        <div class="mdl-card__actions mdl-card--border">
            <router-link :to="cardLink" class="details-button mdl-button">
                Show Details
            </router-link>
        </div>
    </div>
</template>

<script>
import moment from 'moment';

export default {
  name: 'StatusOverviewCard',
  props: ['student-id', 'rubric'],
  data() {
    return {
      now: moment.utc()
    };
  },
  computed: {
    allReviewsCompleted() {
      const {reviewInfo: {completed = null, totalToComplete = null} = {}} = this.rubric;
      const dataPresent = completed !== null && totalToComplete !== null;
      return dataPresent && completed === totalToComplete;
    },
    allReviewsReceived() {
      const {reviewInfo: {received = null, totalToReceive = null} = {}} = this.rubric;
      const dataPresent = received !== null && totalToReceive !== null;
      return dataPresent && received === totalToReceive;
    },
    noReviewsCompleted() {
      const {reviewInfo: {completed = null} = {}} = this.rubric;
      return completed !== null && completed === 0;
    },
    noReviewsReceived() {
      const {reviewInfo: {received = null} = {}} = this.rubric;
      return received !== null && received === 0;
    },
    someCompletedLate() {
      const {reviewInfo: {completedLate = null} = {}} = this.rubric;
      return completedLate !== null && completedLate > 0;
    },
    someReceivedLate() {
      const {reviewInfo: {receivedLate = null} = {}} = this.rubric;
      return receivedLate !== null && receivedLate > 0;
    },
    cardLink() {
      return {
        name: 'AssignmentStatusForRubric',
        params: {
          studentId: this.studentId,
          rubricId: this.rubric.rubricId
        }
      };
    },
    dueDatePassed() {
      return this.now.isSameOrAfter(this.rubric.dueDate);
    },
    reviewProblemsExist() {
      const promptMissing = !this.rubric.reviewInfo.submissionPresent && this.rubric.reviewsWereDistributed;
      return promptMissing || (this.dueDatePassed && (this.noReviewsCompleted || this.noReviewsReceived));
    },
    titleBarClasses() {
      return {
        'mdl-card__title': true,
        'mdl-card--expand': true,
        'title-bar': true,
        'title-bar__issue': this.reviewProblemsExist
      };
    }
  }
};
</script>

<style scoped>
    .status-line {
        display: flex;
        align-items: center;
    }

    .status-line > i {
        margin-right: 10px;
    }

    .title-bar {
        color: white;
        background-color: rgb(63,81,181);
    }

    .title-bar__issue {
        background-color: #DD5465;
    }

    .details-button {
        color: #777777;
        width: 100%;
        box-sizing: border-box;
    }
</style>
