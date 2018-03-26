import api from '@/services/api';
import {navigateToErrorPage} from '@/router/helpers';

export default {
  install(Vue) {
    Vue.mixin({
      beforeCreate() {
        const vm = this;
        this._api = {
          get() {
            return api
              .get
              .apply(vm, arguments)
              .catch(error => navigateToErrorPage(vm, null, error));
          },
          post() {
            return api
              .post
              .apply(vm, arguments)
              .catch(error => navigateToErrorPage(vm, null, error));
          }
        };
      }
    });

    Object.defineProperty(Vue.prototype, '$api', {
      get() {
        return this._api;
      }
    });
  }
};
