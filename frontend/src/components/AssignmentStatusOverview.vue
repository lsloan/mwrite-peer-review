<template>
    <div class="mdl-grid">
        <status-overview-card
            v-for="rubric in rubrics"
            :key="rubric.id"
            :student-id="studentId"
            :rubric="rubric"/>
    </div>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';

import StatusOverviewCard from '@/components/StatusOverviewCard';

const convertRubricDates = r => R.merge(r, {
  dueDate: moment.utc(r.dueDate),
  promptDueDate: moment.utc(r.promptDueDate)
});

export default {
  name: 'AssignmentStatusOverview',
  props: ['student-id'],
  components: {StatusOverviewCard},
  data() {
    return {
      data: {}
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    rubrics() {
      return R.pipe(
        R.map(convertRubricDates),
        R.sortBy(r => r.rubricId)
      )(this.data);
    }
  },
  mounted() {
    this.$api.get('/course/{}/rubric/all/for-student/{}', this.courseId, this.studentId)
      .then(r => {
        this.data = r.data;
      });
  }
};
</script>

<style scoped>
</style>
