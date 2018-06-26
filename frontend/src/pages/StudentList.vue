<template>
    <filterable-table
        :table-name="courseName + ' Students'"
        :entries="entries"
        :column-mapping="columnMapping"
        :is-loading="!Boolean(students)"
        :row-click-handler="goToStudent"
        :make-row-link="makeStudentLink"
        filter-session-storage-key="studentsListFilterValues"/>
</template>

<script>
import * as R from 'ramda';
import * as StudentsService from '@/services/students';
import FilterableTable from '@/components/FilterableTable';

export default {
  name: 'StudentList',
  components: {FilterableTable},
  data() {
    return {
      students: null,
      columnMapping: [
        {
          key: 'name',
          description: 'Student Name',
          transform: R.identity,
          filter: {
            type: 'absolute',
            defaultValue: '',
            predicate: StudentsService.rowMatchesStudentNameFilter,
            saveToSessionStorage: false
          }
        },
        {
          key: 'sections',
          description: 'Sections',
          transform: StudentsService.allSectionsForDisplay,
          filter: {
            type: 'choices',
            defaultValue: StudentsService.ALL_STUDENTS_SECTION,
            makeFilterChoices: StudentsService.entriesToFilterChoices,
            predicate: StudentsService.rowMatchesSectionFilter,
            saveToSessionStorage: true
          }
        }
      ]
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
        ? this.students
          .map(StudentsService.makeStudentEntry)
          .sort(StudentsService.alphabeticalComparator)
        : [];
    }
  },
  methods: {
    makeStudentLink(studentId) {
      return `#/instructor/reviews/student/${studentId}`;
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
