import Vue from 'vue';
import Router from 'vue-router';

import {redirectToRoleDashboard, ensureUserDetailsArePresent, instructorsOnlyGuard} from './guards';
import StudentList from '@/components/StudentList';
import NestedRouteContainer from '@/components/NestedRouteContainer';
import InstructorDashboard from '@/components/InstructorDashboard';

Vue.use(Router);

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
          component: InstructorDashboard,
          meta: {
            breadcrumbPathComponents: [{text: 'Peer Review', href: '/instructor/dashboard'}]
          }
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
