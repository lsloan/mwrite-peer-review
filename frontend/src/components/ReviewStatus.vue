<template>
    <filterable-table
        :table-name="courseName"
        :entries="reviews"
        :is-loading="!Boolean(entries)"
        :column-mapping="columns"
        :row-click-handler="goToReview"
        :mke-row-link="makeReviewLink"
        :filter-session-storage-key="sessionStorageKey"/>
</template>

<script>
import * as R from 'ramda';
import * as StudentsService from '@/services/students';
import FilterableTable from '@/components/FilterableTable';

const makeReviewEntry = review => ({
  id: review.author.id,
  name: review.author.name,
  sections: review.sections,
  reviewsGiven: `${review.completed} of ${review.totalCompleted}`,
  reviewsReceived: `${review.received} of ${review.totalReceived}`
});

export default {
  name: 'review-status',
  props: ['rubric-id'],
  components: {FilterableTable},
  data() {
    return {
      apiUrl: __API_URL__,
      entries: null,
      columns: [
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
        },
        {
          key: 'reviewsGiven',
          description: 'Reviews Given',
          transform: R.identity
        },
        {
          key: 'reviewsReceived',
          description: 'Reviews Received',
          transform: R.identity
        }
      ]
    };
  },
  computed: {
    reviews() {
      return this.entries
        ? this.entries.reviews
          .map(makeReviewEntry)
          .sort(StudentsService.alphabeticalComparator)
        : [];
    },
    sessionStorageKey() {
      return `reviewsForRubric${this.rubricId}FilterValues`;
    },
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    courseName() {
      return this.$store.state.userDetails.courseName;
    }
  },
  methods: {
    makeReviewLink(studentId) {
      return `${this.apiUrl}/course/${this.courseId}/review/student/${studentId}/rubric/${this.rubricId}`;
    },
    goToReview(studentId) {
      window.location = this.makeReviewLink(studentId);
    }
  },
  mounted() {
    this.$api.get('/course/{}/reviews/rubric/{}', this.courseId, this.rubricId).then(r => {
      console.log('rubric status:', r.data);
      this.entries = r.data;
    });
  }
};
</script>

<style scoped>
</style>
