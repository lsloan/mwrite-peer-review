<template>
    <div class="mdl-snackbar mdl-js-snackbar"
         aria-live="assertive"
         aria-atomic="true"
         aria-relevant="text">
        <div class="mdl-snackbar__text" role="alert"></div>
        <button class="mdl-snackbar__action" type="button"></button>
    </div>
</template>

<script>
export const notificationTime = message => 3000 + 120 * message.length;

export default {
  name: 'Snackbar',
  props: {
    displayOn: {
      type: String,
      required: true
    },
    eventSource: {
      type: Object,
      required: false,
      default() {
        return this.$root;
      }
    }
  },
  methods: {
    showSnackbar(message) {
      const config = {
        message,
        timeout: notificationTime(message)
      };
      this.$el.MaterialSnackbar.showSnackbar(config);
    }
  },
  mounted() {
    componentHandler.upgradeElement(this.$el, 'MaterialSnackbar'); // eslint-disable-line no-undef
    this.eventSource.$on(this.displayOn, this.showSnackbar);
  },
  destroyed() {
    this.eventSource.$off(this.displayOn, this.showSnackbar);
  }
};
</script>

<style scoped>
</style>
