<template>
    <div>
        <div class="mdl-grid">
            <h1>TODO student name goes here</h1>
            <mdl-anchor-button raised :href="dataDownloadUrl">
                Download All Data
            </mdl-anchor-button>
        </div>
        <div class="mdl-grid">
            <mdl-tabs v-model="selectedTab" class="tabs">
                <mdl-tab tab="Overview">1</mdl-tab>
                <mdl-tab tab="Two">2</mdl-tab>
                <mdl-tab tab="Three">3</mdl-tab>
            </mdl-tabs>
        </div>
    </div>
</template>

<script>
import {MdlTab, MdlTabs, MdlAnchorButton} from 'vue-mdl';

export default {
  name: 'AssignmentStatus',
  props: ['student-id', 'rubric-id'],
  components: {MdlTab, MdlTabs, MdlAnchorButton},
  data() {
    return {
      selectedTab: 'Overview'
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    dataDownloadUrl() {
      const apiUrl = __API_URL__;
      const baseUrl = `${apiUrl}/course/${this.courseId}/students/${this.studentId}/data/`;
      return this.rubricId ? `${baseUrl}rubric/${this.rubricId}/` : baseUrl;
    }
  }
};
</script>

<style scoped>
    h1 {
        font-family: "Roboto","Helvetica","Arial",sans-serif;
        font-size: 28px;
        line-height: 28px;
        margin: 8px 0;
    }

    .tabs >>> .mdl-tabs__tab-bar {
        justify-content: initial;
    }
</style>
