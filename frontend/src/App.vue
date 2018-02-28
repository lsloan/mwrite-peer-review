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
            <breadcrumb v-if="userIsInstructor" :path-components="breadcrumbPathComponents"/>
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
      return [
        {text: 'One', href: '/one'},
        {text: 'Two', href: '/two'},
        {text: 'Three', href: '/three'}
      ];
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
