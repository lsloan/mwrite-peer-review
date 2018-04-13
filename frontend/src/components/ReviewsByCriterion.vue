<template>
    <div>
        <div class="criterion-entry" v-for="entry in data" :key="entry.id">
            <p class="criterion-name">{{ entry.title }}</p>
            <p class="criterion-description">{{ entry.criterion }}</p>
            <p v-for="comment in entry.entries" :key="comment.id">
                <span class="student-name">{{ comment.reviewerName }}</span>
                <span>{{ comment.text }}</span>
            </p>
        </div>
    </div>
</template>

<script>
export default {
  name: 'reviews-by-criterion',
  props: ['data'],
  mounted() {
    console.log('reviews by criterion:', this.data);
  }
};
</script>

<style scoped>
</style>
