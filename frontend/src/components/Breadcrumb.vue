<template>
    <div class="breadcrumb">
        <breadcrumb-entry
            v-for="({text, href}, i) in pathComponents"
            :key="i"
            :text="text"
            :href="href"
            :is-last-entry="i >= pathComponents.length-1"/>
    </div>
</template>

<script>
import BreadcrumbEntry from '@/components/BreadcrumbEntry';

export default {
  name: 'breadcrumb',
  components: {BreadcrumbEntry},
  props: ['path-components']
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
