import Vue from 'vue';
import Router from 'vue-router';
import multiguard from 'vue-router-multiguard';

import {redirectToRoleDashboard, ensureUserDetailsArePresent, instructorsOnlyGuard} from './guards';
import StudentList from '@/components/StudentList';
import PermissionDenied from '@/components/PermissionDenied';
import InstructorDashboard from '@/components/InstructorDashboard';

Vue.use(Router);

const authenticatedInstructorsOnly = multiguard([ensureUserDetailsArePresent, instructorsOnlyGuard]);

const router = new Router({
  routes: [
    {
      path: '/',
      beforeEnter: redirectToRoleDashboard
    },
    {
      path: '/permission-denied',
      component: PermissionDenied
    },
    {
      path: '/instructor/dashboard',
      component: InstructorDashboard,
      beforeEnter: authenticatedInstructorsOnly,
      meta: {
        breadcrumbPathComponents: [{text: 'Peer Review', href: '/instructor/dashboard'}]
      }
    },
    {
      path: '/instructor/students',
      component: StudentList,
      beforeEnter: authenticatedInstructorsOnly,
      meta: {
        breadcrumbPathComponents: [{text: 'Students', href: '/instructor/students'}]
      }
    }
  ]
});

export default router;
