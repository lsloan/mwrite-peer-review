<template>
    <div class="mdl-grid" v-if="data.promptSubmitted && reviewsWereAssigned">
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
                        :subject-id="studentId"
                        :subject-name="studentFirstName"
                        :subject-email="data.student.email"
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
                        :subject-id="studentId"
                        :subject-name="studentFirstName"
                        :subject-email="data.student.email"
                        :due-date="dueDate"
                        :review="review"/>
                </div>
            </div>
        </div>
        <router-view/>
    </div>
    <div class="centered mdl-grid" v-else>
        <template v-if="!reviewsWereAssigned">
            Peer reviews have not yet been assigned for this prompt.
        </template>
        <template v-else-if="!data.promptSubmitted">
            {{ studentFirstName }} did not submit their prompt assignment, so they will not be able to participate
            in peer review.
        </template>
    </div>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';

import {sortableNameToFirstName} from '@/services/students';
import PeerReviewStatusCard from '@/components/PeerReviewStatusCard';

export default {
  name: 'AssignmentStatusForRubric',
  props: ['student-id', 'rubric-id'],
  components: {PeerReviewStatusCard},
  data() {
    return {
      data: {}
    };
  },
  methods: {
    makeReview(r) {
      return {
        id: r.id,
        rubricId: this.rubricId,
        name: r.student.sortableName,
        email: r.student.email,
        completedAt: r.completedAt ? moment.utc(r.completedAt) : null
      };
    }
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
    reviewsWereAssigned() {
      const {rubric: {reviewsWereAssigned = false} = {}} = this.data;
      return reviewsWereAssigned;
    },
    reviewsToBeCompleted() {
      const {completed = []} = this.data;
      return R.sortBy(r => r.id, completed).map(this.makeReview);
    },
    reviewsToBeReceived() {
      const {received = []} = this.data;
      return R.sortBy(r => r.id, received).map(this.makeReview);
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

    .centered {
        justify-content: center;
    }
</style>
