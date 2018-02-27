import Vue from 'vue';
import Router from 'vue-router';
import store from '@/store';
import HelloWorld from '@/components/HelloWorld';
import RouteGuard from '@/components/RouteGuard';
import StudentList from '@/components/StudentList';
import InstructorDashboard from '@/components/InstructorDashboard';
import DeleteMe from '@/components/DeleteMe';

Vue.use(Router);

const guardTest = (targetRole, to, from, next) => {
  const {roles} = store.state.userDetails;
  const shouldProceed = roles.find(role => role === targetRole);
  next(!!shouldProceed);
};

const authGuard = (targetRole, to, from, next, tryAgain = true) => {
  if('roles' in store.state.userDetails) {
    guardTest(targetRole, to, from, next);
  }
  else if(tryAgain) {
    store.dispatch('fetchUserDetails').then(() => {
      authGuard(targetRole, to, from, next, false);
    });
  }
};

const instructorsOnlyGuard = (to, from, next) => {
  return authGuard('instructor', to, from, next);
};

export default new Router({
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: HelloWorld
    },
    {
      path: '/tryAuth',
      name: 'AuthComponent',
      component: RouteGuard,
      beforeEnter: instructorsOnlyGuard
    },
    {
      path: '/instructor/dashboard',
      component: InstructorDashboard,
      beforeEnter: instructorsOnlyGuard
    },
    {
      path: '/instructor/students',
      component: StudentList,
      beforeEnter: instructorsOnlyGuard
    },
    {
      path: '/instructor/deleteme',
      component: DeleteMe,
      beforeEnter: instructorsOnlyGuard
    }
  ]
});
