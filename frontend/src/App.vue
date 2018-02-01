<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
import api from '@/services/api';
export default {
  name: 'App',
  beforeCreate: function() {
    api.get('/course/15/user/self').then(response => {
      this.$store.commit('userDetails', response.data);
    });
  }
};
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
