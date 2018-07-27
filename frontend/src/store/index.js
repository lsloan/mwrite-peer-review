import Vue from 'vue';
import Vuex from 'vuex';
import api from '@/services/api';

Vue.use(Vuex);

// TODO consider hot reloading; see https://vuex.vuejs.org/en/hot-reload.html

export default new Vuex.Store({
  state: {
    userDetails: {},
    breadcrumbInfo: {},
    reviewsReceived: {}
  },
  mutations: {
    updateUserDetails(state, userDetails) {
      state.userDetails = userDetails;
    },
    updateBreadcrumbInfo(state, breadcrumbInfo) {
      state.breadcrumbInfo = breadcrumbInfo;
    },
    updateReviewsReceived(state, reviewsReceived) {
      state.reviewsReceived = reviewsReceived;
    }
  },
  actions: {
    fetchUserDetails(context) {
      return api.get('/user/self').then(response => context.commit('updateUserDetails', response.data));
    },
    fetchReviewsReceived(context, payload) {
      const {courseId, studentId, rubricId} = payload;
      const apiService = payload.api ? payload.api : api;

      return apiService.get('/course/{}/reviews/student/{}/received/{}', courseId, studentId, rubricId)
        .then(response => context.commit('updateReviewsReceived', response.data));
    },
    submitEvaluation(context, payload) {
      const {courseId, userId, peerReviewId, data} = payload;
      const apiService = payload.api ? payload.api : api;

      return apiService.post('/course/{}/reviews/student/{}/evaluation/{}/', data, courseId, userId, peerReviewId);
    }
  }
});
