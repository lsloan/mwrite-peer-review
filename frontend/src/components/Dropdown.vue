<template>
    <div>
        <!--<label :for="id">{{ label }}</label>-->  <!-- TODO add this back for screen readers only -->
        <div class="dropdown-container">
            <button :id="id" class="dropdown-button" type="button" :disabled="disabled" @click="toggleDropdown">
                <span class="selected-option">{{ displayName }}</span>
                <i class="material-icons dropdown-arrow">arrow_drop_down</i>
            </button>
            <ul v-if="showDropdown" class="menu">
                <li class="menu-item"
                    tabindex="0"
                    v-for="option in options"
                    :key="option.value"
                    @click="selectInput(option)"
                    @keyup.enter="selectInput(option)">
                    {{ option.name }}
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
export default {
  name: 'Dropdown',
  props: ['id', 'value', 'options', 'label', 'disabled', 'empty-caption'],
  data() {
    return {
      showDropdown: false
    };
  },
  computed: {
    displayName: function() {
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
        border: none;
        border-bottom: 1px solid rgba(0,0,0,.12);
        margin-left: 5px;
        cursor: pointer;
        background-color: white;
    }

    .dropdown-button:disabled {
        cursor: initial;
    }

    .selected-option {
        font-size: 16px;
    }

    .dropdown-arrow {
        float: right;
    }

    .dropdown-container {
        position: relative;
    }

    .menu {
        margin: 0px;
        padding: 15px;
        list-style-type: none;
        position: absolute;
        z-index: 100;
        background-color: white;
        box-shadow: 0 2px 2px 0 rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.2), 0 1px 5px 0 rgba(0,0,0,.12);
    }

    .menu-item {
        cursor: pointer;
        padding-top: 5%;
        padding-bottom: 5%;
    }

    .menu-item:hover {
        background-color: lightgray;
    }
</style>
