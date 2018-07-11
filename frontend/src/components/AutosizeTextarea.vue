<template>
    <div class="mdl-textfield mdl-js-textfield">
        <textarea
            :id="_uid"
            ref="textarea"
            class="autosize-textarea mdl-textfield__input"
            rows="1"
            :disabled="disabled"
            @input="$emit('input', $event.target.value)"
            :value="value">
        </textarea>
    <label v-if="label" :for="_uid" class="mdl-textfield__label">{{ label }}</label>
    </div>
</template>

<script>
import autosize from 'autosize';

export default {
  name: 'autosize-textarea',
  props: ['value', 'disabled', 'label'],
  mounted() {
    autosize(this.$refs.textarea);
    componentHandler.upgradeElement(this.$el); // eslint-disable-line no-undef
  },
  updated() {
    this.$el.MaterialTextfield.checkDirty();
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
</style>
