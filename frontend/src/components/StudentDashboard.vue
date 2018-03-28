<template>
    <div>
        <div class="mdl-grid">
            <!-- TODO "assigned to me" section goes here -->
        </div>
        <div class="mdl-grid">
            <!-- TODO "completed work" section goes here -->
        </div>
        <router-link :to="{name: 'SampleModalChild', params: {id: sampleData.id}}">
            open sample modal
        </router-link>
        <router-view/>
    </div>
</template>

<script>
export default {
  name: 'student-dashboard',
  data() {
    return {
      sampleData: {
        id: 1000,
        title: 'Sample Prompt'
      }
    };
  }
};
</script>

<style scoped>
</style>
