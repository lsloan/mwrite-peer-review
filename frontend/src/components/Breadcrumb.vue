<template>
    <div class="breadcrumb">
        <template v-for="({eventKey, text, href}, i) in resolvedPathComponents">
            <breadcrumb-entry
                :key="i"
                :text="text"
                :href="href"
                :is-last-entry="i >= resolvedPathComponents.length-1"/>
        </template>
    </div>
</template>

<script>
import BreadcrumbEntry from '@/components/BreadcrumbEntry';

export default {
  name: 'breadcrumb',
  components: {BreadcrumbEntry},
  props: ['path-components'],
  computed: {
    breadcrumbInfo() {
      return this.$store.state.breadcrumbInfo;
    },
    isDynamic() {
      return typeof this.pathComponents === 'function';
    },
    resolvedPathComponents() {
      if(this.isDynamic) {
        if(this.breadcrumbInfo) {
          return this.pathComponents(this.breadcrumbInfo);
        }
        else {
          return [];
        }
      }
      else {
        return this.pathComponents;
      }
    }
  }
};
</script>

<style scoped>
    .breadcrumb {
        display: flex;
        width: 100%;
        height: 50px;
        line-height: 50px;
        padding-left: 20px;
        background-color: #f8f8f8;
    }
</style>
