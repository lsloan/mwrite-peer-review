<template>
    <div class="mdl-grid" v-if="reviewAssignments && reviewAssignments.length > 0">
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
    <div v-else-if="reviewAssignments && reviewAssignments.length === 0" class="mdl-grid">
        <div class="empty-assignments-container mdl-card mdl-cell mdl-cell--12-col">
            <p>There are currently no peer review assignments.</p>
        </div>
    </div>
</template>

<script>
import PeerReviewAssignmentCard from '@/components/PeerReviewAssignmentCard';

export default {
  components: {PeerReviewAssignmentCard},
  name: 'instructor-dashboard',
  data() {
    return {
      reviewAssignments: null
    };
  },
  mounted() {
    const { courseId } = this.$store.state.userDetails;
    this.$api.get('/course/{0}/peer_review/all', courseId).then(response => {
      this.reviewAssignments = response.data;
    });
  }
};
</script>

<style scoped>
    .empty-assignments-container {
        text-align: center;
    }
</style>
