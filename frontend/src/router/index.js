import Vue from 'vue';
import Router from 'vue-router';
import HelloWorld from '@/components/HelloWorld';
import RouteGuard from '@/components/RouteGuard';

Vue.use(Router);

const authFunc = (to, from, next) => {
  console.log('nope');
  next(false);
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
      beforeEnter: authFunc
    }
  ]
});
