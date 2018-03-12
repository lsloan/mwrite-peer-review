import api from '@/services/api';
import {navigateToErrorPage} from '@/router/helpers';

export default {
  install(Vue) {
    Vue.prototype.$api = function() {
      const vm = this;
      this.$api.get = function() {
        return api.get.apply(vm, arguments).catch(error => navigateToErrorPage(vm, null, error));
      };
      this.$api.post = function() {
        return api.post.apply(vm, arguments).catch(error => navigateToErrorPage(vm, null, error));
      };
    };

    Vue.mixin({
      beforeCreate() {
        this.$api();
      }
    });
  }
};
