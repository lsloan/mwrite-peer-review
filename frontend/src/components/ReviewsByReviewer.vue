<template>
    <mdl-tabs v-model="selectedTab" class="tabs">
        <mdl-tab v-for="entry in data" :key="entry.id" :tab="entry.title">
            <div v-for="subEntry in entry.entries" :key="subEntry.id">
                <p class="heading">{{ subEntry.heading }}</p>
                <p>{{ subEntry.content }}</p>
            </div>
        </mdl-tab>
    </mdl-tabs>
</template>

<script>
import {MdlTab, MdlTabs} from 'vue-mdl';

export default {
  name: 'reviews-by-reviewer',
  props: ['data'],
  components: {MdlTab, MdlTabs},
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
    .heading {
        font-weight: bold;
        margin-bottom: 0;
    }

    .tabs >>> .mdl-tabs__tab-bar {
        border: initial;
        justify-content: initial;
        -webkit-justify-content: initial;
        padding-bottom: 25px;
    }
</style>
