<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--12-col">
                <h2 class="peer-review-title">{{ peerReviewTitle }}</h2>
            </div>
        </div>
        <div class="mdl-grid caption-row">
            <div class="mdl-cell mdl-cell--8-col">
                <p>
                    The students listed below have not been assigned peer reviews because they did not submit their
                    prompt before the due date.  You can allow them to review three random students' submissions, either
                    by choosing their submission status or by selecting individual students below, and then clicking the
                    <strong>Assign</strong> button.  Note that the students you select and assign this way will
                    <strong>not</strong> receive any peer reviews of their submission.
                </p>
            </div>
            <div class="mdl-cell mdl-cell--4-col"></div>
        </div>
        <filterable-table
            :is-loading="isLoading"
            :entries="students"
            :column-mapping="columnMapping"
            :controls="tableControls"/>
        <div class="mdl-grid">
            <button type="button"
                    class="assign-reviews-button mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent"
                    :disabled="studentsToBeAssigned.length === 0"
                    @click="assignReviews">
                Assign Reviews
            </button>
        </div>
    </div>
</template>

<script>
import Vue from 'vue';
import * as R from 'ramda';

import {alphabeticalComparator, rowMatchesStudentNameFilter} from '@/services/students';
import FilterableTable from '@/components/FilterableTable';

import StudentCheckbox from '@/components/StudentCheckbox';

const EventBus = new Vue();
const SELECT_LATE_SUBMITTER_EVENT = 'select-late-submitters';
const SELECT_NON_SUBMITTER_EVENT = 'select-non-submitters';

const COLUMN_MAPPING = [
  {
    component: StudentCheckbox,
    description: '',
    transform: row => ({
      'student-id': row.studentId,
      'student-name': row.studentSortableName,
      'event-bus': EventBus
    })
  },
  {
    key: 'studentSortableName',
    description: 'Student Name',
    transform: R.identity,
    filter: {
      type: 'absolute',
      defaultValue: '',
      predicate: R.partialRight(rowMatchesStudentNameFilter, [R.prop('studentSortableName')]),
      saveToSessionStorage: false
    }
  },
  {
    key: 'studentSections',
    description: 'Sections',
    transform: R.identity
  },
  {
    key: 'submissionState',
    description: 'Submission Status',
    transform: R.identity
  }
];

const TABLE_CONTROLS = [
  {
    key: SELECT_LATE_SUBMITTER_EVENT,
    type: 'button',
    caption: 'Select Late-Submitting Students',
    event: SELECT_LATE_SUBMITTER_EVENT,
    eventBus: EventBus
  },
  {
    key: SELECT_NON_SUBMITTER_EVENT,
    type: 'button',
    caption: 'Select Non-Submitting Students',
    event: SELECT_NON_SUBMITTER_EVENT,
    eventBus: EventBus
  }
];

const submissionStateForStudent = student => {
  if(!student.submitted) {
    return 'not-submitted';
  }
  else if(student.submittedLate) {
    return 'submitted-late';
  }
  else {
    return 'unknown';
  }
};

export default {
  name: 'ManualDistribution',
  props: ['rubric-id'],
  components: {FilterableTable},
  data() {
    return {
      isLoading: true,
      selectedStudents: {},
      data: {},
      columnMapping: COLUMN_MAPPING,
      tableControls: TABLE_CONTROLS
    };
  },
  computed: {
    courseId() {
      const {courseId} = this.$store.state.userDetails;
      return courseId;
    },
    peerReviewTitle() {
      const {peerReviewTitle = '...'} = this.data;
      return peerReviewTitle;
    },
    students() {
      const {students = []} = this.data;
      return students
        .map(s => R.assoc('submissionState', submissionStateForStudent(s), s))
        .sort(R.partialRight(alphabeticalComparator, [R.prop('studentSortableName')]));
    },
    studentsToBeAssigned() {
      const selectedStudents = R.filter(R.identity, this.selectedStudents);
      const selectedStudentIds = R.keys(selectedStudents);
      return selectedStudentIds.map(id => parseInt(id));
    }
  },
  methods: {
    selectStudent({studentId, checked}) {
      Vue.set(this.selectedStudents, studentId, checked);
    },
    assignReviews() {
      // TODO implement this
      console.log('would have assigned review to', this.studentsToBeAssigned);
    }
  },
  mounted() {
    this.$api.get('/course/{}/reviews/rubric/{}/unassigned', this.courseId, this.rubricId)
      .then(response => {
        this.data = response.data;
        this.isLoading = false;
      });
    EventBus.$on('select-student', this.selectStudent);
  },
  destroyed() {
    EventBus.$off('select-student', this.selectStudent);
  }
};
</script>

<style scoped>
    h2.peer-review-title {
        font-size: 24px;
        line-height: 32px;
        margin: 24px 0 0;
    }

    .caption-row {
        padding-right: 0; /* to prevent text reflow when the table dimensions necessitate a scrollbar */
    }

    .assign-reviews-button {
        margin: 0 auto;
    }
</style>
