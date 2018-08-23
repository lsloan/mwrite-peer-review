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
                    :disabled="isLoading || studentsToBeAssigned.length === 0"
                    @click="assignReviews">
                Assign Reviews
            </button>
        </div>
        <mdl-snackbar display-on="notification"/> <!-- TODO replace this with Snackbar component when PR #325 is merged -->
    </div>
</template>

<script>
import Vue from 'vue';
import {MdlSnackbar} from 'vue-mdl'; // TODO replace this with Snackbar component when PR #325 is merged
import * as R from 'ramda';

import {alphabeticalComparator, rowMatchesStudentNameFilter} from '@/services/students';
import FilterableTable from '@/components/FilterableTable';
import StudentCheckbox from '@/components/StudentCheckbox';
import DistributionSubmissionStatus from '@/components/DistributionSubmissionStatus';

const EventBus = new Vue();
const SELECT_LATE_SUBMITTER_EVENT = 'select-late-submitters';
const SELECT_NON_SUBMITTER_EVENT = 'select-non-submitters';

const COLUMN_MAPPING = [
  {
    component: StudentCheckbox,
    description: '',
    transform: row => ({
      'student-id': row.studentId,
      'student-name': row.studentSortableName
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
    description: 'Submission Status',
    component: DistributionSubmissionStatus,
    transform: row => ({
      'submission-status': row.submissionState
    })
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

const SUBMISSION_STATE_NOT_SUBMITTED = 'not-submitted';
const SUBMISSION_STATE_SUBMITTED_LATE = 'submitted-late';
const SUBMISSION_STATE_UNKNOWN = 'unknown';

const submissionStateForStudent = student => {
  if(!student.submitted) {
    return SUBMISSION_STATE_NOT_SUBMITTED;
  }
  else if(student.submittedLate) {
    return SUBMISSION_STATE_SUBMITTED_LATE;
  }
  else {
    return SUBMISSION_STATE_UNKNOWN;
  }
};

export default {
  name: 'ManualDistribution',
  props: ['rubric-id'],
  components: {FilterableTable, MdlSnackbar},
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
      return this.$store.getters.studentsToBeAssignedReviews;
    }
  },
  methods: {
    initializeEventBus() {
      EventBus.$on(SELECT_NON_SUBMITTER_EVENT, this.selectNonSubmittingStudents);
      EventBus.$on(SELECT_LATE_SUBMITTER_EVENT, this.selectLateSubmittingStudents);
    },
    cleanUpEventBus() {
      EventBus.$off(SELECT_NON_SUBMITTER_EVENT, this.selectNonSubmittingStudents);
      EventBus.$off(SELECT_LATE_SUBMITTER_EVENT, this.selectLateSubmittingStudents);
    },
    initializeData() {
      this.$store.commit('resetManualReviewDistribution');
      return this.$api.get('/course/{}/reviews/rubric/{}/unassigned', this.courseId, this.rubricId)
        .then(response => {
          this.data = response.data;
          this.isLoading = false;
        });
    },
    selectStudents(predicate) {
      this.students
        .filter(predicate)
        .map(({studentId}) => studentId)
        .forEach(studentId => {
          this.$store.commit('setStudentForReview', {
            studentId,
            checked: true
          });
        });
    },
    selectNonSubmittingStudents() {
      this.selectStudents(s => s.submissionState === SUBMISSION_STATE_NOT_SUBMITTED);
    },
    selectLateSubmittingStudents() {
      this.selectStudents(s => s.submissionState === SUBMISSION_STATE_SUBMITTED_LATE);
    },
    assignReviews() {
      this.isLoading = true;
      const payload = {
        studentIds: this.studentsToBeAssigned
      };
      this.$api.post('/course/{}/reviews/rubric/{}/assign/', payload, this.courseId, this.rubricId)
        .then(this.initializeData)
        .then(() => {
          this.$root.$emit('notification', {
            message: 'The specified students were successfully assigned reviews.'
          });
        });
    }
  },
  mounted() {
    this.initializeEventBus();
    this.initializeData();
  },
  destroyed() {
    this.cleanUpEventBus();
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
