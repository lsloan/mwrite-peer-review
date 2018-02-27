import Vue from 'vue';
import Router from 'vue-router';

import store from '@/store';
import StudentList from '@/components/StudentList';
import NestedRouteContainer from '@/components/NestedRouteContainer';
import InstructorDashboard from '@/components/InstructorDashboard';

Vue.use(Router);

const hasRoleTest = (targetRole, to, from, next) => {
  const {roles} = store.state.userDetails;
  const shouldProceed = roles.find(role => role === targetRole);
  next(!!shouldProceed);
};

const instructorsOnlyGuard = (to, from, next) => {
  hasRoleTest('instructor', to, from, next);
};

const checkOrFetchUserDetails = (next, tryAgain) => {
  if('roles' in store.state.userDetails) {
    next();
  }
  else if(tryAgain) {
    store.dispatch('fetchUserDetails').then(() => {
      checkOrFetchUserDetails(next, false);
    });
  }
};

const ensureUserDetailsArePresent = (to, from, next) => {
  checkOrFetchUserDetails(next, true);
};

// TODO should use route names here instead of paths?
const redirectToRoleDashboard = (to, from, next) => {
  const {roles} = store.state.userDetails;
  if(roles.includes('instructor')) {
    next('/instructor/dashboard');
  }
  else {
    next(false); // TODO update this when the student dashboard is ported to VueJS
  }
};

const router = new Router({
  routes: [
    {
      path: '/',
      beforeEnter: redirectToRoleDashboard
    },
    {
      path: '/instructor',
      component: NestedRouteContainer,
      beforeEnter: instructorsOnlyGuard,
      children: [
        {
          path: 'dashboard',
          component: InstructorDashboard
        },
        {
          path: 'students',
          component: StudentList
        }
      ]
    }
  ]
});

router.beforeEach(ensureUserDetailsArePresent);

export default router;
