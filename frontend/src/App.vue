<template>
    <div id="app" class="mdl-layout mdl-js-layout">
        <header class="mdl-layout__header">
            <div class="mdl-layout-icon"></div>
            <div class="mdl-layout__header-row">
                <span class="mdl-layout__title">M-Write Peer Review</span>
                <div class="mdl-layout-spacer"></div>
                <nav v-if="userIsInstructor" class="mdl-navigation">
                    <router-link class="mdl-navigation__link" to="/instructor/dashboard">
                        Peer Review
                    </router-link>
                    <!-- TODO change the <a> below to <router-link> when students list is completed -->
                    <a class="mdl-navigation__link" :href="studentsListUrl">
                        Students
                    </a>
                </nav>
            </div>
        </header>
        <main class="mdl-layout__content">
            <breadcrumb
                v-if="userIsInstructor && breadcrumbPathComponents"
                :path-components="breadcrumbPathComponents"/>
            <router-view/>
        </main>
    </div>
</template>

<script>
import Breadcrumb from '@/components/Breadcrumb';

export default {
  name: 'App',
  components: {Breadcrumb},
  computed: {
    breadcrumbPathComponents() {
      // TODO Eventually we'll need to pull data from parameterized routes as well.
      // A lot of that logic will probably be best orchestrated here.  This will
      // also probably need to interact with Vuex as well (e.g. if the user navigates
      // to /instructor/students/1234 we'll need to know the full / sortable name of
      // the student with ID 1234 so that we can put it in the breadcrumb).  I'm sort
      // of envisioning a system whereby we add to the Route object's meta key a
      // function that takes $route.params and the Vuex store as parameters and returns
      // a {text: ..., href: ...} object like the others.
      // This also might end up as a much more flexible / resilient system if we set up
      // some sort of "meta hierarchy" and then walk the route path.  Undoubtedly slower,
      // but it would almost let the breadcrumb derive itself.
      return this.$route.meta.breadcrumbPathComponents;
    },
    userIsInstructor() {
      const {roles} = this.$store.state.userDetails;
      return roles ? roles.includes('instructor') : false;
    },
    studentsListUrl() {
      return __API_URL__ + '/course/' + this.$store.state.userDetails.courseId + '/review/students';
    }
  }
};
</script>

<style>
    .mdl-navigation__link {
        text-transform: uppercase;
    }

    .mdl-layout__header-row {
        padding-left: 20px;
    }
</style>
