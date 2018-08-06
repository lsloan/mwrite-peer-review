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
    manualReviewDistribution: {}
  },
  mutations: {
    userDetails(state, userDetails) {
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
    }
  },
  getters: {
    studentsToBeAssignedReviews(state) {
      const selectedStudents = R.filter(R.identity, state.manualReviewDistribution);
      const selectedStudentIds = R.keys(selectedStudents);
      return selectedStudentIds.map(id => parseInt(id));
    }
  },
  actions: {
    fetchUserDetails(context) {
      return api.get('/user/self').then(response => {
        context.commit('userDetails', response.data);
      });
    }
  }
});
