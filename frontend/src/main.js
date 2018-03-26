import Vue from 'vue';

import VueMdl from 'vue-mdl';
import VueAnalytics from 'vue-analytics';

import App from './App';
import store from '@/store';
import router from '@/router';
import api from '@/plugins/api';

Vue.use(VueMdl);
Vue.use(api);
if(__GA_TRACKING_ID__) {
  Vue.use(VueAnalytics, {
    id: __GA_TRACKING_ID__
  });
}

Vue.config.productionTip = false;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
});
