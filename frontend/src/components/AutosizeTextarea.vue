<template>
    <div class="mdl-textfield mdl-js-textfield">
        <textarea
            :id="_uid"
            class="autosize-textarea mdl-textfield__input"
            type="text"
            rows="1"
            :disabled="disabled"
            @input="$emit('input', $event.target.value)"
            v-model="value"/>
    <label v-if="label" :for="_uid" class="mdl-textfield__label">{{ label }}</label> +
    </div>
</template>

<script>
export default {
  name: 'autosize-textarea',
  props: ['value', 'disabled', 'label']
};
</script>

<style scoped>
</style>
