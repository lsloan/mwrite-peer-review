<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">
                <h2>Assigned work</h2>
                <p>Click "Start Review" to leave feedback.
                    Click "Edit" to revise feedback while the assignment is open.
                    If "Edit" and then "Save" are used after the due date,
                    the submission time for the review will update and the submission will be recorded as late.</p>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>
        <div class="mdl-grid" v-if="prompts.length === 0">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">
                <p>You have no reviews to complete at this time.</p>
            </div>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>
        <div class="mdl-grid" v-else v-for="entry in entries" :key="entry.id">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <work-card
                class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone"
                :title="entry.title"
                :card-type="entry.type"
                :due-date-utc="entry.dueDateUtc"
                :entries="entry.subEntries"
                :make-link="entry.makeLink"/>
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
        </div>
    </div>
</template>

<script>
import * as R from 'ramda';

import {byDateAscending} from '@/services/util';
import WorkCard from '@/components/WorkCard';

const makeEntry = (type, makeLink, title, subEntries, dueDateUtc) => ({
  type,
  makeLink,
  title,
  subEntries,
  dueDateUtc
});

const makeSubEntry = (id, type, isReady, isComplete) => ({
  id,
  type,
  isReady,
  isComplete
});

// TODO combine this with evaluationToEntry?
const promptToEntry = prompt => {
  const sortedReviews = R.sortBy(r => r.reviewId, prompt.reviews);
  const subEntryType = 'review';
  const subEntryConversion = r => makeSubEntry(
    r.reviewId,
    subEntryType,
    true,
    r.reviewIsComplete
  );
  const subEntries = sortedReviews.map(subEntryConversion);
  const makeReviewLink = subEntry => ({
    name: 'PeerReview',
    params: {
      reviewId: subEntry.id
    }
  });
  return makeEntry(subEntryType, makeReviewLink, prompt.promptName, subEntries, prompt.dueDateUtc);
};

// TODO combine this with promptToEntry?
const evaluationToEntry = (reviewerId, peerReview) => {
  const subEntryType = 'evaluation';
  const sortedEvaluations = R.sortBy(e => e.studentId, peerReview.evaluations);
  const subEntryConversion = e => makeSubEntry(
    e.peerReviewId,
    subEntryType,
    e.readyForEvaluation,
    e.evaluationIsComplete
  );
  const subEntries = sortedEvaluations.map(subEntryConversion);
  const makeEvaluateLink = subEntry => ({
    name: 'MandatoryEvaluation',
    params: {
      studentId: reviewerId,
      peerReviewId: subEntry.id
    }
  });
  return makeEntry(subEntryType, makeEvaluateLink, peerReview.peerReviewTitle, subEntries, peerReview.dueDateUtc);
};

export default {
  name: 'AssignedWork',
  props: ['prompts', 'evaluations'],
  components: {WorkCard},
  computed: {
    userId() {
      return this.$store.state.userDetails.userId;
    },
    promptEntries() {
      return this.prompts.map(promptToEntry);
    },
    evaluationEntries() {
      const conversion = R.partial(evaluationToEntry, [this.userId]);
      return this.evaluations.map(conversion);
    },
    entries() {
      const entries = this.promptEntries.concat(this.evaluationEntries);
      return entries.sort(byDateAscending);
    },
    courseId() {
      return this.$store.state.userDetails.courseId;
    }
  }
};
</script>

<style scoped>
    h2 {
        font-size: 24px;
        margin: 4px 0;
        font-weight: bolder;
        line-height: 1.35;
        letter-spacing: -0.02em;
    }
</style>
