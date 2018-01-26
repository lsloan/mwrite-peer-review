export default {
  install(Vue, options) {
    Vue.prototype.$userDetails = {roles: null};
  }
};
