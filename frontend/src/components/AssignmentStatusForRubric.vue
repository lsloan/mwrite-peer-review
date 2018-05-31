<template>
    <div class="mdl-grid">
        <div class="mdl-cell mdl-cell--6-col">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--12-col"><h1>Reviews Completed</h1></div>
            </div>
            <div class="mdl-grid">
                <peer-review-status-card v-for="(_, index) in reviewsToBeCompleted" :key="index"/>
            </div>
        </div>
        <div class="mdl-cell mdl-cell--6-col">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--12-col"><h1>Reviews Received</h1></div>
            </div>
            <div class="mdl-grid">
                <peer-review-status-card v-for="(_, index) in reviewsToBeReceived" :key="index"/>
            </div>
        </div>
    </div>
</template>

<script>
import PeerReviewStatusCard from '@/components/PeerReviewStatusCard';

export default {
  name: 'AssignmentStatusForRubric',
  props: ['student-id', 'rubric-id'],
  components: {PeerReviewStatusCard},
  data() {
    return {
      reviewsToBeCompleted: [1, 2, 3],
      reviewsToBeReceived: [1, 2, 3]
    };
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
