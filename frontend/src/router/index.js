import Vue from 'vue';
import Router from 'vue-router';
import HelloWorld from '@/components/HelloWorld';
import RouteGuard from '@/components/RouteGuard';
import StudentList from '@/components/StudentList';
import DeleteMe from '@/components/DeleteMe';

Vue.use(Router);

const authGuard = (targetRole, to, from, next) => {
  const userRoles = this.a.app.$userDetails.roles;
  const go = userRoles.find((role) => role === targetRole);
  next(!!go);
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
