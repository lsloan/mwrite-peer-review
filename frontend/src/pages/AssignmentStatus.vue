<template>
    <div>
        <div class="mdl-grid">
            <h1>{{ studentName }}</h1>
            <div class="mdl-layout-spacer"></div>
            <mdl-anchor-button class="data-download-button" raised :href="dataDownloadUrl">
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
        <assignment-status-overview v-if="!rubricId" :student-id="studentId"/>
        <assignment-status-for-rubric v-else :student-id="studentId" :rubric-id="rubricId" :key="rubricId"/>
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
      data: {}
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    studentName() {
      const {studentInfo: {fullName = ''} = {}} = this.data;
      return fullName;
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

      const {rubrics = []} = this.data;
      const promptEntries = rubrics.map(r => ({
        to: {
          name: 'AssignmentStatusForRubric',
          params: {
            studentId: this.studentId,
            rubricId: r.id
          }
        },
        title: r.promptTitle,
        isActivePred: rId => r.id === rId
      }));

      return [overviewEntry].concat(promptEntries);
    },
    dataDownloadUrl() {
      const apiUrl = __API_URL__;
      const baseUrl = `${apiUrl}/course/${this.courseId}/students/${this.studentId}/data/`;
      return this.rubricId ? `${baseUrl}rubric/${this.rubricId}/` : baseUrl;
    }
  },
  mounted() {
    Promise.all([
      this.$api.get('/course/{}/students/{}/', this.courseId, this.studentId),
      this.$api.get('/course/{}/rubric/all/', this.courseId)
    ]).then(([{data: studentInfo}, {data: rubrics}]) => {
      this.data = {
        studentInfo: studentInfo,
        rubrics: rubrics
      };
    });
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

    .data-download-button {
        margin-top: 5px;
    }

    .mdl-tabs__tab-bar {
        justify-content: initial;
    }

    .active-tab {
        /* TODO MDL's slide-in bottom border would be great, but is suprisingly complicated. later */
        border-bottom: 2px solid rgb(63,81,181);
    }
</style>
