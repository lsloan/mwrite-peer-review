<template>
    <transition name="modal">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container">

                    <div class="modal-header">
                        <span class="modal-title">{{ title }}</span>
                        <mdl-button @click.native="closeModal" class="modal-close-button mdl-button--icon">
                            <i class="material-icons">close</i>
                        </mdl-button>
                    </div>

                    <div class="modal-body">
                        <component :is="component" v-bind="childProps" v-on:title-resolved="setTitle"/>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>

<script>
import {MdlButton} from 'vue-mdl';

export default {
  name: 'modal',
  props: ['component', 'child-props'],
  components: {MdlButton},
  data() {
    return {
      title: ''
    };
  },
  methods: {
    closeModal() {
      this.$router.back();
    },
    setTitle(title) {
      this.title = title;
    }
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

    .modal-title {
        flex-grow: 1;
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
