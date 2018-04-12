<template>
  <div>
    <label :for="id">{{ label }}</label>
    <button :id="id" type="button" class="mdl-button mdl-js-button"     :disabled="disabled">
      <span>{{ displayName }}</span>
    </button>
    <ul :for="id" class="mdl-menu mdl-js-menu">
      <li tabindex="0" class="mdl-menu__item" v-for="option in options" :key="option.value" @click="$emit('input', option)">
          {{ option.name }}
      </li>
    </ul>
  </div>
</template>

<script>

export default {
  name: 'Dropdown',
  computed: {
    displayName: function() {
      console.log('DROPDOWN: value: ', this.value, ' and ', this.value.name);
      console.log('DROPDOWN return val: ', (this.value && this.value.name));
      return (this.value && this.value.name) || this.emptyCaption;
    }
  },
  props: ['id', 'value', 'options', 'label', 'disabled', 'empty-caption'],
  mounted: function() {
    // eslint-disable-next-line no-undef
    componentHandler.upgradeElement(this.$el.querySelector('button'));
  }

};
</script>

<style scoped>
.mdl-button {
  border-bottom: solid thin lightgray;
  margin-left: 5px;
}
</style>
