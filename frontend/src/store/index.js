import * as R from 'ramda';
import Vue from 'vue';
import Vuex from 'vuex';

import api from '@/services/api';

Vue.use(Vuex);

// TODO consider hot reloading; see https://vuex.vuejs.org/en/hot-reload.html

export default new Vuex.Store({
  state: {
    userDetails: {},
    breadcrumbInfo: {},
    manualReviewDistribution: {},
    commentsById: {},
    pendingEvaluations: []
  },
  getters: {
    commentsBy(state) {
      const comments = R.values(state.commentsById);
      return {
        rubric: R.pipe(
          R.groupBy(c => c.rubricId),
          R.map(comments => ({
            'reviewer': R.groupBy(c => c.reviewerId, comments),
            'criterion': R.groupBy(c => c.criterionId, comments)
          }))
        )(comments),
        peerReview: R.groupBy(c => c.peerReviewId, comments)
      };
    },
    studentsToBeAssignedReviews(state) {
      const selectedStudents = R.filter(R.identity, state.manualReviewDistribution);
      const selectedStudentIds = R.keys(selectedStudents);
      return selectedStudentIds.map(id => parseInt(id));
    }
  },
  mutations: {
    updateUserDetails(state, userDetails) {
      state.userDetails = userDetails;
    },
    updateBreadcrumbInfo(state, breadcrumbInfo) {
      state.breadcrumbInfo = breadcrumbInfo;
    },
    resetManualReviewDistribution(state) {
      state.manualReviewDistribution = {};
    },
    setStudentForReview(state, {studentId, checked}) {
      Vue.set(state.manualReviewDistribution, studentId, checked);
    },
    mergeComments(state, newCommentsById) {
      state.commentsById = R.merge(state.commentsById, newCommentsById);
    },
    updatePendingEvaluations(state, pendingEvaluations) {
      state.pendingEvaluations = pendingEvaluations;
    },
    markEvaluationCompleteForReview(state, peerReviewId) {
      const evaluation = state.pendingEvaluations.find(e => e.peerReviewId === peerReviewId);
      evaluation.evaluationIsComplete = true;
    }
  },
  actions: {
    fetchUserDetails(context) {
      return api.get('/user/self').then(response => context.commit('updateUserDetails', response.data));
    },
    fetchCommentsForRubric(context, payload) {
      const {courseId, studentId, rubricId} = payload;
      const apiService = payload.api ? payload.api : api;
      return apiService.get('/course/{}/reviews/student/{}/received/{}', courseId, studentId, rubricId)
        .then(response => context.commit('mergeComments', response.data));
    },
    fetchCommentsForReview(context, payload) {
      const {courseId, peerReviewId} = payload;
      const apiService = payload.api ? payload.api : api;
      return apiService.get('/course/{}/reviews/{}', courseId, peerReviewId)
        .then(response => context.commit('mergeComments', response.data));
    },
    submitEvaluation(context, payload) {
      const {courseId, userId, peerReviewId, data} = payload;
      const apiService = payload.api ? payload.api : api;

      return apiService.post('/course/{}/reviews/student/{}/evaluation/{}/', data, courseId, userId, peerReviewId);
    },
    fetchPendingEvaluations(context, payload) {
      const {courseId, userId} = payload;
      const apiService = payload.api ? payload.api : api;

      apiService.get('/course/{}/reviews/student/{}/evaluation/pending', courseId, userId)
        .then(response => context.commit('updatePendingEvaluations', response.data));
    }
  }
});
