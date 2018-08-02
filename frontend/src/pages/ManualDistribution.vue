<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--12-col">
                <h2 class="peer-review-title">{{ peerReviewTitle }}</h2>
            </div>
        </div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--8-col">
                <p>
                    The students listed below have not been assigned peer reviews because they did not submit their
                    prompt before the due date.  You can allow them to review three random students' submissions, either
                    by choosing their submission status or by selecting individual students below, and then clicking the
                    <strong>Assign</strong> button.  Note that the students you select and assign this way will
                    <strong>not</strong> receive any peer reviews of their submission.
                </p>
            </div>
            <div class="mdl-cell mdl-cell--4-col"></div>
        </div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--12-col">
                <p>TODO table for rubric {{rubricId}} goes here</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
  name: 'ManualDistribution',
  props: ['rubric-id'],
  data() {
    return {
      data: {}
    };
  },
  computed: {
    courseId() {
      const {courseId} = this.$store.state.userDetails;
      return courseId;
    },
    peerReviewTitle() {
      const {peerReviewTitle = '...'} = this.data;
      return peerReviewTitle;
    }
  },
  mounted() {
    this.$api.get('/course/{}/reviews/rubric/{}/unassigned', this.courseId, this.rubricId)
      .then(response => {
        this.data = response.data;
      });
  }
};
</script>

<style scoped>
    h2.peer-review-title {
        font-size: 24px;
        line-height: 32px;
        margin: 24px 0 0;
    }
</style>
