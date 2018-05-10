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

// TODO should find a better value than 0 here?
const allStudentsSectionId = 0;

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

// TODO put the R.reduce curry here
const combineEntrySections = (acc, next) => {
  const sections = next.sections;

  for(let i = 0; i < sections.length; i++) {
    if(!acc.hasOwnProperty(sections[i].id)) {
      acc[sections[i]['id']] = sections[i].name;
    }
  }

  return acc;
};

// TODO see above
const entriesToFilterChoices = entries => {
  const sectionsById = entries.reduce(combineEntrySections, {});
  sectionsById[allStudentsSectionId] = 'All Students';
  return Object.entries(sectionsById)
    .map(([id, name]) => ({value: parseInt(id), name: name}))
    .sort((a, b) => a.value - b.value);
};

export default {
  name: 'StudentList',
  components: {FilterableTable},
  data() {
    return {
      apiUrl: __API_URL__,
      students: null,
      columnMapping: [
        {
          key: 'name',
          description: 'Student Name',
          transform: R.identity,
          filter: {
            type: 'absolute',
            defaultValue: '',
            predicate: (value, entry) => value === '' || entry.name.includes(value)
          }
        },
        {
          key: 'sections',
          description: 'Sections',
          transform: allSectionsForDisplay,
          filter: {
            type: 'choices',
            defaultValue: {'value': allStudentsSectionId, 'name': 'All Students'},
            makeFilterChoices: entriesToFilterChoices,
            predicate: (value, entry) => value.value === allStudentsSectionId || entry.sections.includes(value)
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
