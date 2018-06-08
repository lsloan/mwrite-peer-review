<template>
    <filterable-table
        class="review-status-table"
        :table-name="courseName"
        :entries="reviews"
        :row-classes="rowClasses"
        :is-loading="!Boolean(data)"
        :column-mapping="columns"
        :row-click-handler="goToReview"
        :mke-row-link="makeReviewLink"
        :filter-session-storage-key="sessionStorageKey"/>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';
import * as StudentsService from '@/services/students';
import FilterableTable from '@/components/FilterableTable';

const makeReviewEntry = review => ({
  id: review.author.id,
  name: review.author.name,
  sections: review.sections,
  reviewsGiven: {
    completed: review.completed,
    total: review.totalCompleted
  },
  reviewsReceived: {
    completed: review.received,
    total: review.totalCompleted
  }
});

const reviewsForDisplay = r => `${r.completed} of ${r.total}`;

export default {
  name: 'review-status',
  props: ['rubric-id'],
  components: {FilterableTable},
  data() {
    return {
      data: null,
      pageLoadTime: null,
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
          transform: reviewsForDisplay
        },
        {
          key: 'reviewsReceived',
          description: 'Reviews Received',
          transform: reviewsForDisplay
        }
      ]
    };
  },
  computed: {
    peerReviewDueDate() {
      if(this.data) {
        return moment(this.data.rubric.peerReviewDueDate).utc();
      }
    },
    rowClasses() {
      return {
        'late-review': row => {
          if(this.peerReviewDueDate) {
            const dueDatePassed = this.peerReviewDueDate.isBefore(this.pageLoadTime);
            if(dueDatePassed) {
              const {reviewsReceived, reviewsGiven} = row;
              const noReviewsReceived = reviewsReceived.completed === 0;
              const noReviewsGiven = reviewsGiven.completed === 0;
              return noReviewsReceived || noReviewsGiven;
            }
          }
        }
      };
    },
    reviews() {
      return this.data
        ? this.data.reviews
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
      return `#/instructor/reviews/student/${studentId}/rubric/${this.rubricId}`;
    },
    goToReview(studentId) {
      window.location = this.makeReviewLink(studentId);
    }
  },
  mounted() {
    this.pageLoadTime = moment().utc();
    this.$api.get('/course/{}/reviews/rubric/{}', this.courseId, this.rubricId)
      .then(r => {
        this.data = r.data;
      })
      .then(() => {
        this.$store.commit('updateBreadcrumbInfo', {
          title: `${this.data.rubric.peerReviewTitle} Reviews`,
          rubricId: this.data.rubric.id
        });
      });
  }
};
</script>

<style scoped>
    .review-status-table >>> tr.late-review {
      background-color: #F9EAEC;
    }

    .review-status-table >>> tr.late-review:hover {
      background-color: rgb(255, 168, 180);
    }
</style>
