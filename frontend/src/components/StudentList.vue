<template>
    <filterable-table
        :table-name="courseName"
        :entries="entries"
        :column-mapping="columnMapping"
        :is-loading="!Boolean(students)"
        :row-click-handler="goToStudent"
        :make-row-link="makeStudentLink"
        section-filter-session-storage-key="studentsListSection"/>
</template>

<script>
import * as R from 'ramda';
import FilterableTable from '@/components/FilterableTable';

const makeStudentEntry = student => ({
  id: student.id,
  name: student.sortableName,
  sections: student.sections
});

const alphabeticalComparator = (a, b) => {
  if(a.name.toLowerCase() < b.name.toLowerCase()) {
    return -1;
  }
  if(a.name.toLowerCase() > b.name.toLowerCase()) {
    return 1;
  }
  return 0;
};

const namesFromSections = ss => ss.map(s => s.name);

const allSectionsForDisplay = R.pipe(
  namesFromSections,
  R.intersperse(', '),
  R.reduce(R.concat, '')
);

export default {
  name: 'StudentList',
  components: {FilterableTable},
  data() {
    return {
      students: null,
      apiUrl: __API_URL__,
      columnMapping: [
        {key: 'name', description: 'Student Name', transform: R.identity},
        {key: 'sections', description: 'Sections', transform: allSectionsForDisplay}
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
