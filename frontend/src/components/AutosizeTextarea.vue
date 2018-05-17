<template>
    <div class="mdl-textfield mdl-js-textfield">
        <textarea
            :id="_uid"
            class="autosize-textarea mdl-textfield__input"
            type="text"
            rows="1"
            :disabled="disabled"
            @input="$emit('input', $event.target.value)"
            :value="value"/>
    <label v-if="label" :for="_uid" class="mdl-textfield__label">{{ label }}</label>
    </div>
</template>

<script>
import autosize from 'autosize';

export default {
  name: 'autosize-textarea',
  props: ['value', 'disabled', 'label'],
  mounted() {
    autosize(this.$el.querySelector('textarea'));
    componentHandler.upgradeElement(this.$el); // eslint-disable-line no-undef
  },
  updated() {
    this.$el.MaterialTextfield.checkDirty();
  }
};
</script>

<style scoped>
</style>
