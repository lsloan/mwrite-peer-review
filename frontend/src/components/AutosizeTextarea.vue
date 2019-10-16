<template>
    <textarea
        :id="_uid"
        ref="textarea"
        class="autosize-textarea"
        rows="2"
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
    if(this.$attrs.value) { // trigger 'input' event to make Vue.js update its field values
      this.$el.dispatchEvent((new Event('input')));
    }
    autosize(this.$refs.textarea);
    componentHandler.upgradeElement(this.$el); // eslint-disable-line no-undef
  },
  updated() {
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
