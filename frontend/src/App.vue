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
import * as R from 'ramda';

import Breadcrumb from '@/components/Breadcrumb';

const routeIsForModal = r => R.find(
  ro => {
    let {name = ''} = ro.components.default;
    return name.toLowerCase() === 'modal';
  },
  r.matched
);

export default {
  name: 'App',
  components: {Breadcrumb},
  computed: {
    breadcrumbPathComponents() {
      const lens = R.lensPath(['meta', 'breadcrumbPathComponents']);
      const route = R.findLast(R.view(lens), this.$route.matched);
      if(route) {
        const {meta: {breadcrumbPathComponents} = {}} = route;
        return breadcrumbPathComponents;
      }
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
      if(!routeIsForModal(from) && !routeIsForModal(to)) {
        this.$store.commit('updateBreadcrumbInfo', null);
      }
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
