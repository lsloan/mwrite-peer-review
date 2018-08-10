<template>
    <mdl-tabs v-model="selectedTab" class="tabs">
        <mdl-tab v-for="entry in data" :key="entry.id" :tab="entry.title">
            <review-by-reviewer :allow-evaluation="allowEvaluation" :review="entry"/>
        </mdl-tab>
    </mdl-tabs>
</template>

<script>
import {MdlTab, MdlTabs} from 'vue-mdl';

import ReviewByReviewer from '@/components/ReviewByReviewer';

export default {
  name: 'reviews-by-reviewer',
  props: ['data', 'allow-evaluation'],
  components: {MdlTab, MdlTabs, ReviewByReviewer},
  data() {
    return {
      selectedTab: ''
    };
  },
  watch: {
    data() {
      if(this.data.length > 0) {
        this.selectedTab = this.data[0].title;
      }
    }
  }
};
</script>

<style scoped>
    .tabs >>> .mdl-tabs__tab-bar {
        border: initial;
        justify-content: initial;
        -webkit-justify-content: initial;
        padding-bottom: 25px;
    }
</style>
