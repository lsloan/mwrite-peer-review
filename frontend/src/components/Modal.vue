<template>
    <transition name="modal">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div ref="modal"
                     class="modal-container"
                     role="dialog"
                     aria-labelledby="modal-title"
                     @keyup.esc="closeModal"
                     @keydown.tab="handleTab">

                    <div class="modal-header">
                        <div class="modal-titles-container">
                            <span id="modal-title" ref="title" class="modal-title" tabindex="-1">{{ title }}</span>
                            <span class="modal-subtitle" v-if="subtitle">{{ subtitle }}</span>
                        </div>
                        <mdl-button @click.native="closeModal" class="modal-close-button mdl-button--icon">
                            <i class="material-icons">close</i>
                        </mdl-button>
                    </div>

                    <div class="modal-body">
                        <component
                            :is="component"
                            v-bind="childProps"
                            v-on:title-resolved="setTitle"
                            v-on:subtitle-resolved="setSubtitle"/>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>

<script>
import {MdlButton} from 'vue-mdl';

const TABS_CLASS = '.mdl-tabs';
const TAB_BODY_CLASS = '.mdl-tabs__panel';
const TAB_BAR_CLASS = '.mdl-tabs__tab-bar';
const TAB_ACTIVE_CLASS = '.is-active';
const TAB_IS_ACTIVE_CLASS = `${TAB_BODY_CLASS}${TAB_ACTIVE_CLASS}`;
const FOCUSABLE_SELECTOR_HEADER = '.modal-header > button, .modal-header > a, .controls button';
const FOCUSABLE_SELECTOR_TABS = `${FOCUSABLE_SELECTOR_HEADER}, ${TAB_BAR_CLASS} a, ${TAB_IS_ACTIVE_CLASS} a, ${TAB_IS_ACTIVE_CLASS} button, ${TAB_IS_ACTIVE_CLASS} input, ${TAB_IS_ACTIVE_CLASS} [tabindex]:not([tabindex="-1"])`;
const FOCUSABLE_SELECTOR_NO_TABS = 'a, button, [tabindex]';

const getTabbableElements = modal => {
  const selector = modal.querySelector(TABS_CLASS)
    ? FOCUSABLE_SELECTOR_TABS
    : FOCUSABLE_SELECTOR_NO_TABS;
  return modal.querySelectorAll(selector);
};

export default {
  name: 'modal',
  props: ['component', 'child-props'],
  components: {MdlButton},
  data() {
    return {
      title: '',
      subtitle: null,
      firstFocusableElement: null,
      lastFocusableElement: null
    };
  },
  methods: {
    closeModal() {
      this.$router.back();
    },
    handleTab(event) {
      this.updateTabbableItems();
      if(event.shiftKey) {
        this.tabPrevious(event);
      }
      else {
        this.tabNext(event);
      }
    },
    tabPrevious() {
      if(document.activeElement === this.firstFocusableElement) {
        this.lastFocusableElement.focus();
        event.preventDefault();
      }
    },
    tabNext(event) {
      if(document.activeElement === this.lastFocusableElement) {
        this.firstFocusableElement.focus();
        event.preventDefault();
      }
    },
    setTitle(title) {
      this.title = title;
    },
    setSubtitle(subtitle) {
      this.subtitle = subtitle;
    },
    focusModalTitle() {
      this.$refs.title.focus();
    },
    updateTabbableItems() {
      const tabbableElements = getTabbableElements(this.$refs.modal);
      this.firstFocusableElement = tabbableElements[0];
      this.lastFocusableElement = tabbableElements[tabbableElements.length - 1];
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.focusModalTitle();
    });
  }
};
</script>

<style scoped>
    .modal-mask {
        position: fixed;
        z-index: 9998;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, .5);
        display: table;
        transition: opacity .3s ease;
    }

    .modal-wrapper {
        display: table-cell;
        vertical-align: middle;
    }

    .modal-container {
        width: 75vw;
        height: 60vh;
        margin: 0 auto;
        background-color: rgb(255, 255, 255);
        border-radius: 2px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
        transition: all .3s ease;
        font-family: Helvetica, Arial, sans-serif;
        display: flex;
        flex-direction: column;
    }

    .modal-header {
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 0 20px;
        background-color: rgb(63, 81, 181);
        color: rgb(255, 255, 255);
        flex: 0 0 64px;
    }

    .modal-titles-container {
        flex-grow: 1;
    }

    .modal-title {
        margin-right: 5px;
        line-height: 25px;
    }

    .modal-subtitle {
        border: 1px solid white;
        border-radius: 2px;
        padding: 4px;
        font-weight: lighter;
        font-size: 12px;
        white-space: nowrap;
    }

    .modal-close-button {
        flex-shrink: 0;
    }

    .modal-body {
        flex: 1;
        min-height: 0;
        overflow-y: auto;
    }

    /* transition="modal" styles below -- see https://vuejs.org/v2/guide/transitions.html */

    .modal-enter {
        opacity: 0;
    }

    .modal-leave-active {
        opacity: 0;
    }

    .modal-enter .modal-container, .modal-leave-active .modal-container {
        -webkit-transform: scale(1.1);
        transform: scale(1.1);
    }
</style>
