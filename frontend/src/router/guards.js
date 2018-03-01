import store from '@/store';
import {checkOrFetchUserDetails, hasRoleTest} from './helpers';

// TODO should use route names here instead of paths?
export const redirectToRoleDashboard = (to, from, next) => {
  checkOrFetchUserDetails(null, true)
    .then(() => {
      const {roles} = store.state.userDetails;
      if(roles.includes('instructor')) {
        next('/instructor/dashboard');
      }
      else if(roles.includes('student')) {
        next('/student/dashboard');
      }
      else {
        next(false);
      }
    })
    .catch(error => {
      if(error.response.status === 403) {
        next('/permission-denied');
      }
      else {
        next(false);
      }
    });
};

export const ensureUserDetailsArePresent = (to, from, next) => {
  checkOrFetchUserDetails(next, true);
};

export const instructorsOnlyGuard = (to, from, next) => {
  hasRoleTest('instructor', to, from, next);
};
