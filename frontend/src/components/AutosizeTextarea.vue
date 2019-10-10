<template>
        <textarea
            :id="_uid"
            ref="textarea"
            class="autosize-textarea"
            rows="1"
            :disabled="disabled"
            @input="$emit('input', $event.target.value)"
            :placeholder="label"
            :value="value">
        </textarea>
</template>

<script>
import autosize from 'autosize';

export default {
  name: 'autosize-textarea',
  props: ['value', 'disabled', 'label'],
  mounted() {
    this.$el.value = this.$attrs.value || ''; // Vue.js textarea value bug workaround
    autosize(this.$refs.textarea);
    componentHandler.upgradeElement(this.$el); // eslint-disable-line no-undef
  },
  updated() {
    /*
     * TODO: try to emit 'input' event at right time if textarea has a default value
     * That may trigger validation and allow user to submit changes without visiting
     * and updating each field of the form first
     *
     * emit() example from PeerReview.vue:
     *
     *         this.$root.$emit('notification', SUBMIT_REVIEW_INCOMPLETE_MESSAGE);
     */
  },
  watch: {
    value() {
      this.$nextTick(() => {
        // see https://github.com/jackmoore/autosize/issues/364
        autosize.update(this.$refs.textarea);
      });
    }
  }
};
</script>

<style scoped>
    .mdl-textfield__label {
        color: #767676;
    }
</style>
