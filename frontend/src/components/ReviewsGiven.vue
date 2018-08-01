<template>
    <div class="reviews-body">
        <reviews-by-reviewer :allow-evaluation="false" :data="reviewEntries"/>
    </div>
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
      this.reviewEntries = entries.map(e => {
        e.title = `Student ${e.studentId + 1}`;
        return e;
      });
      this.title = title;
      this.$emit('title-resolved', this.title);
      this.$emit('subtitle-resolved', 'Reviews Given');
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
    .reviews-body {
        padding: 10px 20px;
    }
</style>
