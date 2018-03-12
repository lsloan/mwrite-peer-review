import store from '@/store';
import {checkOrFetchUserDetails, hasRoleTest, navigateToErrorPage} from './helpers';

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
    .catch(error => navigateToErrorPage(null, next, error));
};

export const ensureUserDetailsArePresent = (to, from, next) => {
  const promiseOrNothing = checkOrFetchUserDetails(next, true);
  if(promiseOrNothing) {
    promiseOrNothing.catch(error => navigateToErrorPage(null, next, error));
  }
};

export const instructorsOnlyGuard = (to, from, next) => {
  hasRoleTest('instructor', to, from, next);
};
