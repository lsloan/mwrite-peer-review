<template>
  <div>
    <h2>Title will go here</h2>
    <div>
      <div>
        <div></div>
        <div></div>
      </div>
      <v-client-table :data='formatData' :columns='cols' :options='options'></v-client-table>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import Vue from 'vue';
import { ClientTable } from 'vue-tables-2';
Vue.use(ClientTable, {}, false, 'bootstrap3', 'default');

export default {
  name: 'StudentList',
  data() {
    return {
      cols: ['name', 'section'],
      options: {
        filterByColumn: true,
        filterable: ['name', 'section'],
        listColumns: {
          section: [
            {id: 1, text: 'Section 1'},
            {id: 2, text: 'Section 2'}
          ]
        },
        headings: {
          name: 'Student Name',
          section: 'Section'
        }
      },
      json_data: {}
    };
  },
  computed: {
    formatData() {
      const origData = this.json_data;
      var formattedData = [];
      for(var i = 0; i < origData.length; i++) {
        formattedData.push({name: origData[i]['fullName'] + ' (' + origData[i]['username'] + ')', section: origData[i]['sections']});
      }
      console.log('new data ', formattedData);

      return formattedData;
    }
  },
  methods: {
    getStudents() {
      api.get('/course/15/students').then((response) => {
        console.log('response: ', response.data);
        this.json_data = response.data;
      });
    }
  },
  created: function() {
    this.getStudents();
  }
};
</script>

<style scoped>

table {
  font: red;
}
</style>
