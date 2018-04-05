<template>
    <reviews-by-reviewer :data="reviewEntries"/>
</template>

<script>
import ReviewsByReviewer from '@/components/ReviewsByReviewer';

export default {
  name: 'reviews-given',
  props: ['student-id', 'rubric-id'],
  components: {ReviewsByReviewer},
  data() {
    return {
      title: '',
      reviewEntries: []
    };
  },
  methods: {
    setData({entries, title}) {
      this.reviewEntries = entries;
      this.title = title;
      this.$emit('title-resolved', this.title);
    }
  },
  mounted() {
    const courseId = this.$store.state.userDetails.courseId;
    this.$api.get('/course/{}/reviews/student/{}/given/{}', courseId, this.studentId, this.rubricId)
      .then(response => this.setData(response.data));
  }
};
</script>

<style scoped>
</style>
