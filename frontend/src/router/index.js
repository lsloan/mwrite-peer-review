import Vue from 'vue';
import Router from 'vue-router';

import {redirectToRoleDashboard, authenticatedInstructorsOnly, authenticatedStudentsOnly} from './guards';

import Modal from '@/components/Modal';
import ReviewsGiven from '@/components/ReviewsGiven';
import ReviewsReceived from '@/components/ReviewsReceived';

import Error from '@/pages/Error';
import InstructorDashboard from '@/pages/InstructorDashboard';
import StudentList from '@/pages/StudentList';
import ReviewStatus from '@/pages/ReviewStatus';
import Rubric from '@/pages/Rubric';
import StudentDashboard from '@/pages/StudentDashboard';
import PeerReview from '@/pages/PeerReview';

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
      name: 'InstructorDashboard',
      component: InstructorDashboard,
      beforeEnter: authenticatedInstructorsOnly,
      meta: {
        breadcrumbPathComponents: [{text: 'Peer Review', href: '/instructor/dashboard'}]
      }
    },
    {
      path: '/instructor/rubric/peer_review_assignment/:peerReviewAssignmentId',
      name: 'Rubric',
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
    },
    {
      name: 'PeerReview',
      path: '/student/review/:reviewId',
      component: PeerReview,
      beforeEnter: authenticatedStudentsOnly,
      props: route => ({reviewId: route.params.reviewId})
    }
  ]
});

export default router;
