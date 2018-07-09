<template>
    <div id="app" class="mdl-layout mdl-js-layout">
        <header class="mdl-layout__header">
            <div class="mdl-layout-icon"></div>
            <div class="mdl-layout__header-row">
                <span class="mdl-layout__title">M-Write Peer Review</span>
                <div class="mdl-layout-spacer"></div>
                <nav v-if="userIsInstructor" class="mdl-navigation">
                    <router-link
                        :class="{'mdl-navigation__link': true, 'is-active': navTreeHead === 'Peer Review'}"
                        to="/instructor/dashboard">
                        Peer Review
                    </router-link>
                    <router-link
                        :class="{'mdl-navigation__link': true, 'is-active': navTreeHead === 'Students'}"
                        to="/instructor/students">
                        Students
                    </router-link>
                </nav>
              </div>
        </header>
        <header>
            <breadcrumb
                v-if="showBreadcrumb"
                :path-components="resolvedBreadcrumbPathComponents"/>
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
    breadcrumbInfo() {
      return this.$store.state.breadcrumbInfo;
    },
    breadcrumbIsDynamic() {
      return typeof this.breadcrumbPathComponents === 'function';
    },
    resolvedBreadcrumbPathComponents() {
      if(this.breadcrumbIsDynamic) {
        if(this.breadcrumbInfo) {
          return this.breadcrumbPathComponents(this.breadcrumbInfo);
        }
        else {
          return [];
        }
      }
      else {
        return this.breadcrumbPathComponents;
      }
    },
    navTreeHead() {
      if(this.resolvedBreadcrumbPathComponents) {
        const [{text = ''} = {}] = this.resolvedBreadcrumbPathComponents;
        console.log('nav tree head =', text);
        return text;
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

    .mdl-navigation__link.is-active {
        /* TODO MDL's slide-in bottom border would be great, but is suprisingly complicated. later */
        border-bottom: 4px solid #c9ffff;
    }

    .mdl-layout__header-row {
        padding-left: 20px;
    }
</style>
