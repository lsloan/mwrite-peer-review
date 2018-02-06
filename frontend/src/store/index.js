import Vue from 'vue';
import Vuex from 'vuex';
import api from '@/services/api';

Vue.use(Vuex);

// TODO consider hot reloading; see https://vuex.vuejs.org/en/hot-reload.html

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
      api.get('/user/self').then(response => {
        context.commit('userDetails', response.data);
      });
    }
  }
});
