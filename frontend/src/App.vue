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
    api.get('/user_roles').then((response) => {
      this.$userDetails.roles = response.data.roles;
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
