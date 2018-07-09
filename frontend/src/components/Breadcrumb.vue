<template>
    <div class="breadcrumb">
        <template v-for="({eventKey, text, href}, i) in pathComponents">
            <breadcrumb-entry
                :key="i"
                :text="text"
                :href="href"
                :is-last-entry="i >= pathComponents.length-1"/>
        </template>
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
