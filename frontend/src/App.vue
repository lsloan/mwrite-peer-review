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
                    <router-link class="mdl-navigation__link" to="/instructor/students">
                        Students
                    </router-link>
                </nav>
              </div>
        </header>
        <header>
            <breadcrumb
                v-if="showBreadcrumb"
                :path-components="breadcrumbPathComponents"/>
        </header>
        <main class="mdl-layout__content">
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
      return this.$route.meta.breadcrumbPathComponents;
    },
    userIsInstructor() {
      const {roles} = this.$store.state.userDetails;
      return roles ? roles.includes('instructor') : false;
    },
    showBreadcrumb() {
      return this.userIsInstructor && this.breadcrumbPathComponents;
    }
  },
  watch: {
    $route(to, from) {
      this.$store.commit('updateBreadcrumbInfo', null);
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
