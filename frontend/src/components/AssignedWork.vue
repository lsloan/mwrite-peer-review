<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--2-col mdl-cell--1-col-tablet mdl-cell--hide-phone"></div>
            <div class="mdl-cell mdl-cell--8-col mdl-cell--6-col-tablet mdl-cell--4-col-phone">
                <h1>Assigned to me</h1>
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
import { sortBy } from 'ramda';

import {byDateAscending} from '@/services/util';
import WorkCard from '@/components/WorkCard';

const makeEntry = (type, makeLink, title, subEntries, dueDateUtc) => ({
  type,
  makeLink,
  title,
  subEntries,
  dueDateUtc
});

const makeSubEntry = (id, type, isComplete) => ({
  id,
  type,
  isComplete
});

// TODO combine this with evaluationToEntry?
const promptToEntry = prompt => {
  const sortedReviews = sortBy(r => r.reviewId, prompt.reviews);
  const subEntries = sortedReviews.map(r => makeSubEntry(r.reviewId, 'review', r.reviewIsComplete));
  const makeReviewLink = subEntry => ({
    name: 'PeerReview',
    params: {
      reviewId: subEntry.id
    }
  });
  return makeEntry('review', makeReviewLink, prompt.promptName, subEntries, prompt.dueDateUtc);
};

// TODO combine this with promptToEntry?
const evaluationToEntry = peerReview => {
  const sortedEvaluations = sortBy(e => e.studentId, peerReview.evaluations);
  const subEntries = sortedEvaluations.map(e => makeSubEntry(e.id, 'evaluation', e.evaluationIsComplete));
  const makeEvaluateLink = subEntry => ({
    // TODO eval route object goes here
  });
  return makeEntry('evaluation', makeEvaluateLink, peerReview.peerReviewTitle, subEntries, peerReview.dueDateUtc);
};

export default {
  name: 'AssignedWork',
  props: ['prompts', 'evaluations'],
  components: {WorkCard},
  computed: {
    promptEntries() {
      return this.prompts.map(promptToEntry);
    },
    evaluationEntries() {
      return this.evaluations.map(evaluationToEntry);
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
    h1 {
        font-size: 24px;
        margin: 4px 0;
        font-weight: bolder;
    }
</style>
