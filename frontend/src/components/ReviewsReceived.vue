<template>
    <div>
        <div class="controls">
            <span>View by:</span>
            <button @click="viewBy = 'student'">Student</button>
            <button @click="viewBy = 'criterion'">Criteria</button>
        </div>
        <keep-alive>
            <reviews-by-reviewer v-if="viewBy === 'student'" :data="data"/>
            <reviews-by-criterion v-else-if="viewBy === 'criterion'" :data="data"/>
        </keep-alive>
    </div>
</template>

<script>
import ReviewsByReviewer from '@/components/ReviewsByReviewer';
import ReviewsByCriterion from '@/components/ReviewsByCriterion';
import {groupBy} from 'ramda';

export default {
  name: 'reviews-received',
  props: ['student-id', 'rubric-id'],
  components: {ReviewsByReviewer, ReviewsByCriterion},
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
          return Object.entries(commentsByReviewer).map(entry => {
            const [reviewerId, comments] = entry;
            return {
              id: reviewerId,
              title: `Student ${comments[0].reviewerId + 1}`,
              entries: comments.map(c => ({id: c.commentId, heading: c.criterion, content: c.comment})) // TODO sort comments?
            };
          });
        }
        else if(this.viewBy === 'criterion') {
          const commentsByCriterion = groupBy(entry => entry.criterionId, this.unfilteredData.entries);
          return Object.entries(commentsByCriterion).map(entry => {
            const [criterionId, comments] = entry;
            return {
              id: criterionId,
              title: `Criterion ${comments[0].criterionId + 1}`,
              entries: comments.map(c => ({id: c.commentId, reviewerName: `Student ${c.reviewerId + 1}`, text: c.comment}))
            };
          });
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
