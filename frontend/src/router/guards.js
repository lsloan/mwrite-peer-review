import multiguard from 'vue-router-multiguard';

import store from '@/store';
import {checkOrFetchUserDetails, hasRoleTest, navigateToErrorPage} from './helpers';

const ensureUserDetailsArePresent = (to, from, next) => {
  checkOrFetchUserDetails(next, true).catch(error => navigateToErrorPage(null, next, error));
};

const instructorsOnlyGuard = (to, from, next) => {
  hasRoleTest('instructor', to, from, next);
};

const studentsOnlyGuard = (to, from, next) => {
  hasRoleTest('student', to, from, next);
};

export const authenticatedInstructorsOnly = multiguard([ensureUserDetailsArePresent, instructorsOnlyGuard]);
export const authenticatedStudentsOnly = multiguard([ensureUserDetailsArePresent, studentsOnlyGuard]);

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
