<template>
    <div>
        <div class="mdl-grid">
            <h1>TODO student name goes here</h1>
            <mdl-anchor-button raised :href="dataDownloadUrl">
                Download
                <template v-if="rubricId">
                    Prompt
                </template>
                <template v-else>
                    All
                </template>
                Data
            </mdl-anchor-button>
        </div>
        <div class="mdl-grid">
            <div class="mdl-tabs">
                <transition-group name="assignment-tabs" tag="div" class="mdl-tabs__tab-bar">
                    <router-link v-for="({title, to, isActivePred}, index) in prompts"
                                 :key="index"
                                 :to="to"
                                 :class="{'mdl-tabs__tab': true, 'active-tab': isActivePred(rubricId)}">
                        {{ title }}
                    </router-link>
                </transition-group>
            </div>
        </div>
        <div class="mdl-grid">
            <assignment-status-overview v-if="!rubricId" :student-id="studentId"/>
            <assignment-status-for-rubric v-else :student-id="studentId" :rubric-id="rubricId"/>
        </div>
    </div>
</template>

<script>
import {MdlAnchorButton} from 'vue-mdl';

import AssignmentStatusOverview from '@/components/AssignmentStatusOverview';
import AssignmentStatusForRubric from '@/components/AssignmentStatusForRubric';

export default {
  name: 'AssignmentStatus',
  props: ['student-id', 'rubric-id'],
  components: {MdlAnchorButton, AssignmentStatusOverview, AssignmentStatusForRubric},
  data() {
    return {
      selectedPrmopt: null,
      data: {},
      tempRubrics: [{id: 1, prompt: 'Prompt One'}, {id: 2, prompt: 'Prompt Two'}]
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    prompts() {
      const overviewEntry = {
        to: {
          name: 'AssignmentStatus',
          params: {
            studentId: this.studentId
          }
        },
        title: 'Overview',
        isActivePred: rubricId => !rubricId
      };
      const promptEntries = this.tempRubrics.map(r => ({
        to: {
          name: 'AssignmentStatusForRubric',
          params: {
            studentId: this.studentId,
            rubricId: r.id
          }
        },
        title: r.prompt,
        isActivePred: rId => r.id === rId
      }));
      return [overviewEntry].concat(promptEntries);
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

    .mdl-tabs__tab-bar {
        justify-content: initial;
    }

    .active-tab {
        /* TODO MDL's slide-in bottom border would be great, but is suprisingly complicated. later */
        border-bottom: 2px solid rgb(63,81,181);
    }
</style>
