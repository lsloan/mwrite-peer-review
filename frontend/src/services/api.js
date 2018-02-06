import Axios from 'axios';
import format from 'string-format';

const defaultOptions = {
  withCredentials: true
};

const defaultPostOptions = Object.assign({
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken'
}, defaultOptions);

const parameterizeURL = (endpoint, params) => {
  const formattedPath = params ? format(endpoint, ...params) : endpoint;
  return __API_URL__ + formattedPath;
};

export default {
  get(endpoint, ...params) {
    const url = parameterizeURL(endpoint, params);
    return Axios.get(url, defaultOptions);
  },
  post(endpoint, data, ...params) {
    const url = parameterizeURL(endpoint, params);
    return Axios.post(url, data, defaultPostOptions);
  }
};
