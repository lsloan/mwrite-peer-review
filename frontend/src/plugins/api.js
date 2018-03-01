import api from '@/services/api';

// TODO see if we can pull this handler off the component itself
const navigateToErrorPage = (vm, error) => {
  if(error.response.status === 403) {
    vm.$router.push('/permission-denied');
  }
  throw error;
};

export default {
  install(Vue) {
    Vue.prototype.$api = function() {
      const vm = this;
      this.$api.get = function() {
        return api.get.apply(vm, arguments).catch(error => navigateToErrorPage(vm, error));
      };
      this.$api.post = function() {
        return api.post.apply(vm, arguments).catch(error => navigateToErrorPage(vm, error));
      };
    };

    Vue.mixin({
      beforeCreate() {
        this.$api();
      }
    });
  }
};
