<template>
    <filterable-table
        :table-name="courseName"
        :entries="students || []"
        :is-loading="!Boolean(students)"
        :row-click-handler="goToStudent"
        :make-row-link="makeStudentLink"
        section-filter-storage-key="studentsListSection"/>
</template>

<script>
import FilterableTable from '@/components/FilterableTable';

export default {
  name: 'RefactoredStudentList',
  components: {FilterableTable},
  data() {
    return {
      students: null,
      apiUrl: __API_URL__
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    courseName() {
      return this.$store.state.userDetails.courseName;
    }
  },
  methods: {
    makeStudentLink(studentId) {
      return `${this.apiUrl}/course/${this.courseId}/review/student/${studentId}`;
    },
    goToStudent(studentId) {
      window.location = this.makeStudentLink(studentId);
    }
  },
  mounted() {
    const {courseId} = this.$store.state.userDetails;
    this.$api.get('/course/{}/students', courseId).then(r => {
      this.students = r.data;
    });
  }
};
</script>

<style scoped>
</style>
