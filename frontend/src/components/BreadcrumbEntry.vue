<template>
    <div>
        <router-link v-if="href && !isLastEntry" :to="href" class="entry-link">{{ text }}</router-link>
        <span v-else class="entry-text">{{ text }}</span>
        <span v-if="!isLastEntry" class="entry-text">/&nbsp;</span>
    </div>
</template>

<script>
export default {
  name: 'breadcrumb-entry',
  props: {
    text: String,
    href: {
      type: String,
      default: null
    },
    isLastEntry: Boolean,
    separator: {
      type: String,
      default: '/'
    }
  }
};
</script>

<style scoped>
    .entry-text {
        color: #b2b2b2;
    }

    .entry-link {
        color: #56c1f2;
        text-decoration: none;
    }
</style>
