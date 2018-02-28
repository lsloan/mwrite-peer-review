<template>
    <div class="mdl-grid">
        <peer-review-assignment-card
            v-for="assignment in reviewAssignments"
            :key="assignment.peerReviewAssignmentId"
            :peer-review-assignment-id="assignment.peerReviewAssignmentId"
            :peer-review-title="assignment.peerReviewTitle"
            :rubric-id="assignment.rubricId"
            :reviews-in-progress="assignment.reviewsInProgress"
            :due-date="assignment.dueDate"
            :open-date="assignment.openDate"
            :validation-info="assignment.validationInfo"
            date-format="MMMM D h:mm A"/>
    </div>
</template>

<script>
import moment from 'moment';
import api from '../services/api';
import PeerReviewAssignmentCard from './PeerReviewAssignmentCard';

const convertDateStringsToMoments = assignment => {
  const {dueDate, openDate} = assignment;
  assignment.dueDate = dueDate ? moment(dueDate).local() : null;
  assignment.openDate = openDate ? moment(openDate).local() : null;
  return assignment;
};

export default {
  components: {PeerReviewAssignmentCard},
  props: ['assignments'],
  name: 'instructor-dashboard',
  data() {
    return {
      reviewAssignments: []
    };
  },
  mounted() {
    const { courseId } = this.$store.state.userDetails;
    api.get('/course/{0}/peer_review/all', courseId).then(response => {
      this.reviewAssignments = response.data.map(convertDateStringsToMoments);
    });
  }
};
</script>

<style scoped>
</style>
