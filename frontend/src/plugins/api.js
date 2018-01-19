import Axios from 'axios';

const defaultOptions = {
  withCredentials: true
};

const defaultPostOptions = Object.assign({
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken'
}, defaultOptions);

const APIPlugin = {
  install(Vue, options) {
    Vue.prototype.$api = {
      get(endpoint) {
        return Axios.get(__API_URL__ + endpoint, defaultOptions);
      },
      post(endpoint, data) {
        return Axios.post(__API_URL__ + endpoint, data, defaultPostOptions);
      }
    };
  }
};

export default APIPlugin;
