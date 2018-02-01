import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    userDetails: {}
  },
  mutations: {
    userDetails(state, userDetails) {
      state.userDetails = userDetails;
    }
  }
});
