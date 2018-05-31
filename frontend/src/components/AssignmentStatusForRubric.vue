<template>
    <div class="mdl-grid">
        <div class="mdl-cell mdl-cell--6-col">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--12-col">
                    <h1>
                        {{ studentFirstName }}
                        completed
                        {{ numberOfCompletedReviews }}/{{ reviewsToBeCompleted.length }}
                        peer reviews
                    </h1>
                </div>
            </div>
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--12-col">
                    <peer-review-status-card
                        v-for="review in reviewsToBeCompleted"
                        :key="review.id"
                        direction="To"
                        :subject="studentFirstName"
                        :due-date="dueDate"
                        :review="review"/>
                </div>
            </div>
        </div>
        <div class="mdl-cell mdl-cell--6-col">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--12-col">
                    <h1>
                        {{ studentFirstName }}
                        received
                        {{ numberOfReceivedReviews }}/{{ reviewsToBeReceived.length }}
                        peer reviews
                    </h1>
                </div>
            </div>
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--12-col">
                    <peer-review-status-card
                        v-for="review in reviewsToBeReceived"
                        :key="review.id"
                        direction="From"
                        :subject="studentFirstName"
                        :due-date="dueDate"
                        :review="review"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';

import {sortableNameToFirstName} from '@/services/students';
import PeerReviewStatusCard from '@/components/PeerReviewStatusCard';

const makeReview = r => ({
  id: r.id,
  name: r.student.sortableName,
  completedAt: r.completedAt ? moment.utc(r.completedAt) : null
});

export default {
  name: 'AssignmentStatusForRubric',
  props: ['student-id', 'rubric-id'],
  components: {PeerReviewStatusCard},
  data() {
    return {
      data: {}
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    studentFirstName() {
      const {student: {sortableName} = {}} = this.data;
      return sortableName
        ? sortableNameToFirstName(sortableName)
        : '';
    },
    dueDate() {
      const {rubric: {peerReviewDueDate} = {}} = this.data;
      return peerReviewDueDate ? moment.utc(peerReviewDueDate) : null;
    },
    reviewsToBeCompleted() {
      const {completed = []} = this.data;
      return R.sortBy(r => r.id, completed).map(makeReview);
    },
    reviewsToBeReceived() {
      const {received = []} = this.data;
      return R.sortBy(r => r.id, received).map(makeReview);
    },
    numberOfCompletedReviews() {
      return this.reviewsToBeCompleted.filter(r => r.completedAt).length;
    },
    numberOfReceivedReviews() {
      return this.reviewsToBeReceived.filter(r => r.completedAt).length;
    }
  },
  mounted() {
    this.$api.get('/course/{}/rubric/{}/for-student/{}', this.courseId, this.rubricId, this.studentId)
      .then(r => {
        console.log(r.data);
        this.data = r.data;
      });
  }
};
</script>

<style scoped>
    h1 {
        font-family: "Roboto","Helvetica","Arial",sans-serif;
        font-size: 28px;
        line-height: 28px;
        margin: 8px 0;
    }
</style>
