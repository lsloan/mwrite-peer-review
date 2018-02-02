<template>
  <div id="app">
    <div>nav bar will go here</div>
    <router-view/>
  </div>
</template>

<script>
import api from '@/services/api';
// import {ServerTable, ClientTable, Event} from 'vue-tables-2';
// import {ClientTable} from 'vue-tables-2';
// Vue.use(ClientTable, {}, false, 'bootstrap3', 'default');
// Vue.use(ClientTable);
// console.log('ClientTable: ', ClientTable);
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
