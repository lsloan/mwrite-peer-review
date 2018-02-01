import Vue from 'vue';
import Vuex from 'vuex';
import api from '@/services/api';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    userDetails: {}
  },
  mutations: {
    userDetails(state, userDetails) {
      state.userDetails = userDetails;
    }
  },
  actions: {
    fetchUserDetails(context) {
      api.get('/course/15/user/self').then(response => {
        context.commit('userDetails', response.data);
      });
    }
  }
});
