<template>
    <label ref="checkbox-root" class="mdl-checkbox mdl-js-checkbox" :for="controlId">
        <input type="checkbox" :id="controlId" class="mdl-checkbox__input" v-model="checked">
        <span class="mdl-checkbox__label hidden-for-sighted-users">Distribute for {{ studentName }}</span>
    </label>
</template>

<script>
export default {
  name: 'StudentCheckbox',
  props: ['student-id', 'student-name', 'event-bus'],
  data() {
    return {
      checked: false
    };
  },
  computed: {
    controlId() {
      return `checkbox-${this.studentId}`;
    }
  },
  mounted() {
    componentHandler.upgradeElement(this.$el); // eslint-disable-line no-undef
  },
  watch: {
    checked(value) {
      const eventBus = this.eventBus || this;
      eventBus.$emit('select-student', {
        studentId: this.studentId,
        checked: value
      });
    }
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
