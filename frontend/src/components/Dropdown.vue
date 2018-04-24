<template>
  <div>
    <label>{{ label }}</label>
    <button class='dropdown-button' type='button' :disabled='disabled' @click='toggleDropdown'>
      <span>{{ displayName }}</span>
      <i class='material-icons'>arrow_drop_down</i>
    </button>
    <ul v-if='showDropdown' class='menu'>
      <li class='menu-item' tabindex='0' v-for='option in options' :key='option.value' @click='selectInput(option)' @keyup.enter='selectInput(option)'>
          {{ option.name }}
      </li>
    </ul>
  </div>
</template>

<script>

export default {
  name: 'Dropdown',
  props: ['id', 'value', 'options', 'label', 'disabled', 'empty-caption'],
  data() {
    return {
      showDropdown: true
    };
  },
  computed: {
    displayName: function() {
      console.log('DROPDOWN: value: ', this.value, ' and ', this.value.name);
      console.log('DROPDOWN return val: ', (this.value && this.value.name));
      return (this.value && this.value.name) || this.emptyCaption;
    }
  },
  methods: {
    selectInput(option) {
      this.$emit('input', option);
      this.showDropdown = false;
    },
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    }
  }
};
</script>

<style scoped>
.dropdown-button {
  border-bottom: 1px solid rgba(0,0,0,.12);
  margin-left: 5px;
}

.menu {
  list-style-type: none;
/*  opacity: 0;
  z-index: -1;*/
}
</style>
