import store from '@/store';
import {checkOrFetchUserDetails, hasRoleTest} from './helpers';

// TODO should use route names here instead of paths?
export const redirectToRoleDashboard = (to, from, next) => {
  const {roles} = store.state.userDetails;
  if(roles.includes('instructor')) {
    next('/instructor/dashboard');
  }
  else {
    next(false); // TODO update this when the student dashboard is ported to VueJS
  }
};

export const ensureUserDetailsArePresent = (to, from, next) => {
  checkOrFetchUserDetails(next, true);
};

export const instructorsOnlyGuard = (to, from, next) => {
  hasRoleTest('instructor', to, from, next);
};
