import Vue from 'vue';
import Vuex from 'vuex';
import api from '@/services/api';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    userDetails: {}
  },
  mutations: {
    fetchUserDetails(state) {
      api.get('/course/15/user/self').then((response) => {
        state.userDetails = response.data;
      });
    }
  }
});
