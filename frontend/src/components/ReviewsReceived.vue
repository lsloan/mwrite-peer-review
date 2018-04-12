<template>
    <div>
        <div class="controls">
            <span>View by:</span>
            <button @click="viewBy = 'student'">Student</button>
            <button @click="viewBy = 'criteria'">Criteria</button>
        </div>
        <keep-alive>
            <reviews-by-reviewer v-if="viewBy === 'student'" :data="data"/>
            <!-- TODO reviews by criteria goes here-->
        </keep-alive>
    </div>
</template>

<script>
import ReviewsByReviewer from '@/components/ReviewsByReviewer';
import {groupBy} from 'ramda';

export default {
  name: 'reviews-received',
  props: ['student-id', 'rubric-id'],
  components: {ReviewsByReviewer},
  data() {
    return {
      viewBy: 'student',
      unfilteredData: null
    };
  },
  computed: {
    data() {
      if(this.unfilteredData) {
        if(this.viewBy === 'student') {
          const commentsByReviewer = groupBy(entry => entry.reviewerId, this.unfilteredData.entries);
          return Object.values(commentsByReviewer).map(cs => {
            return {
              title: `Student ${cs[0].reviewerId + 1}`,
              entries: cs.map(c => ({heading: c.criterion, content: c.comment})) // TODO sort comments?
            };
          });
        }
        else {
          return [];
        }
      }
    }
  },
  methods: {
    setData(data) {
      // TODO remove this
      console.log(data);
      window.data = data;

      this.unfilteredData = data;
      this.$emit('title-resolved', this.unfilteredData.title);
    }
  },
  mounted() {
    const courseId = this.$store.state.userDetails.courseId;
    this.$api.get('/course/{}/reviews/student/{}/received/{}', courseId, this.studentId, this.rubricId)
      .then(response => this.setData(response.data));
  }
};
</script>

<style scoped>

</style>
