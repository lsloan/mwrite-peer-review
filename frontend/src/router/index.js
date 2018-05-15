import Vue from 'vue';
import Router from 'vue-router';

import {redirectToRoleDashboard, authenticatedInstructorsOnly, authenticatedStudentsOnly} from './guards';

import Modal from '@/components/Modal';
import ReviewsGiven from '@/components/ReviewsGiven';
import ReviewsReceived from '@/components/ReviewsReceived';

import Error from '@/pages/Error';
import InstructorDashboard from '@/pages/InstructorDashboard';
import StudentDashboard from '@/pages/StudentDashboard';
import StudentList from '@/pages/StudentList';
import ReviewStatus from '@/pages/ReviewStatus';
import Rubric from '@/pages/Rubric';

Vue.use(Router);

const router = new Router({
  routes: [
    {
      path: '/',
      beforeEnter: redirectToRoleDashboard
    },
    {
      path: '/error',
      component: Error
    },
    {
      path: '/permission-denied',
      component: Error,
      props: {errorMessage: 'You do not have permission to visit that page. Please try logging in again.'}
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
      path: '/instructor/rubric/peer_review_assignment/:peerReviewAssignmentId',
      component: Rubric,
      beforeEnter: authenticatedInstructorsOnly,
      // TODO needs breadcrumbPathComponents
      props: (route) => ({peerReviewAssignmentId: route.params.peerReviewAssignmentId})
    },
    {
      path: '/instructor/students',
      component: StudentList,
      beforeEnter: authenticatedInstructorsOnly,
      meta: {
        breadcrumbPathComponents: [{text: 'Students', href: '/instructor/students'}]
      }
    },
    {
      path: '/instructor/reviews/rubric/:rubricId',
      name: 'ReviewStatus',
      component: ReviewStatus,
      beforeEnter: authenticatedInstructorsOnly,
      props: (route) => ({rubricId: route.params.rubricId})
      // TODO needs breadcrumbPathComponents
    },
    {
      path: '/student/dashboard',
      component: StudentDashboard,
      beforeEnter: authenticatedStudentsOnly,
      children: [
        {
          path: 'student/:studentId/reviews/:rubricId/given/',
          name: 'ReviewsGiven',
          component: Modal,
          props: (route) => ({component: ReviewsGiven, childProps: route.params})
        },
        {
          path: 'student/:studentId/reviews/:rubricId/received/',
          name: 'ReviewsReceived',
          component: Modal,
          props: (route) => ({component: ReviewsReceived, childProps: route.params})
        }
      ]
    }
  ]
});

export default router;
