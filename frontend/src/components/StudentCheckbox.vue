<template>
    <label ref="checkbox-root" class="mdl-checkbox mdl-js-checkbox" :for="controlId">
        <input type="checkbox" :id="controlId" class="mdl-checkbox__input" v-model="checked">
        <span class="mdl-checkbox__label hidden-for-sighted-users">Distribute for {{ studentName }}</span>
    </label>
</template>

<script>
export default {
  name: 'StudentCheckbox',
  props: ['student-id', 'student-name'],
  computed: {
    controlId() {
      return `checkbox-${this.studentId}`;
    },
    checked: {
      get() {
        return this.$store.state.manualReviewDistribution[this.studentId];
      },
      set(checked) {
        const studentId = this.studentId;
        this.$store.commit('setStudentForReview', {studentId, checked});
      }
    }
  },
  mounted() {
    componentHandler.upgradeElement(this.$el); // eslint-disable-line no-undef
  }
};
</script>

<style scoped>
    .hidden-for-sighted-users {
        position:absolute;
        left:-10000px;
        top:auto;
        width:1px;
        height:1px;
        overflow:hidden;
    }
</style>
