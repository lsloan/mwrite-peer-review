<template>
    <filterable-table
        :table-name="courseName"
        :entries="entries"
        :is-loading="!Boolean(students)"
        :row-click-handler="goToStudent"
        :make-row-link="makeStudentLink"
        section-filter-storage-key="studentsListSection"/>
</template>

<script>
import FilterableTable from '@/components/FilterableTable';

const makeStudentEntry = (student) => {
  const sectionNamesIds = student.sections.reduce((acc, next) => {
    acc.ids.push(next.id);
    acc.names.push(next.name);
    return acc;
  }, {ids: [], names: []});

  return {
    id: student.id,
    name: student.sortableName,
    sections: sectionNamesIds
  };
};

const alphabeticalComparator = (a, b) => {
  if(a.name.toLowerCase() < b.name.toLowerCase()) {
    return -1;
  }
  if(a.name.toLowerCase() > b.name.toLowerCase()) {
    return 1;
  }
  return 0;
};

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
    },
    entries() {
      return this.students
        ? this.students.map(makeStudentEntry).sort(alphabeticalComparator)
        : [];
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
