<template>
  <div>
    <h2>Title will go here</h2>
    <div>
      <div>
        <div>filter by section part</div>
        <div>filter by name part</div>
      </div>
      <v-client-table :data='formatData' :columns='cols' :options='options'></v-client-table>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import { ClientTable } from 'vue-tables-2';
Vue.use(ClientTable, {}, false, 'bootstrap3', 'default');

export default {
  name: 'StudentList',
  data() {
    return {
      fake_data: [{
        student: {
          first_name: 'name1',
          last_name: 'ZlastName1'
        },
        section: '1'
      },
      {
        student: {
          first_name: 'name2',
          last_name: 'lastName2'
        },
        section: 'filterval'
      }
      ],
      cols: ['name', 'section'],
      options: {
        headings: {
          name: 'Student Name',
          section: 'Section'
        }
      }
    };
  },
  computed: {
    formatData() {
      const origData = this.fake_data;
      var formattedData = [];
      for(var i = 0; i < origData.length; i++) {
        formattedData.push({name: origData[i]['student']['first_name'] + ' ' + origData[i]['student']['last_name'], section: origData[i]['section']});
      }

      console.log('new data: ', formattedData);
      return formattedData;
    }
  }

};
</script>

<style scoped>
</style>
