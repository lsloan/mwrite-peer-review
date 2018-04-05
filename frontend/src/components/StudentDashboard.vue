<template>
    <div>
        <div class="mdl-grid">
            <!-- TODO "assigned to me" section goes here -->
        </div>
        <div class="mdl-grid">
            <!-- TODO "completed work" section goes here -->
        </div>
        <router-link :to="{name: 'ReviewsGiven', params: {studentId: studentId, rubricId: 1}}">
            open sample reviews given modal
        </router-link>
        <router-view/>
    </div>
</template>

<script>
export default {
  name: 'student-dashboard',
  computed: {
    studentId() {
      return this.$store.state.userDetails.userId;
    }
  }
};
</script>

<style scoped>
</style>
