<template>
  <div>
    <h2>Title will go here</h2>
    <div>
      <div>
        <div></div>
        <div></div>
      </div>
      <v-client-table name='studentTable' :data='formatData' :columns='cols' :options='options' ></v-client-table>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import Vue from 'vue';
import { ClientTable, Event } from 'vue-tables-2';
Vue.use(ClientTable, {}, false, 'bootstrap3', 'default');
Vue.use(Event);

export default {
  name: 'StudentList',
  data() {
    return {
      cols: ['name', 'section'],
      options: {
        filterByColumn: true,
        filterable: ['name', 'section'],
        customFilters: [{
          name: 'section',
          callback: (row, query) => {
            console.log('triggering custom filter, this: ', this);
            this.customSectionFilter(row, query);
          }
        }],
        listColumns: {
          section: [
            {id: 1, text: 'Section 1'},
            {id: 2, text: 'Section 2'},
            {id: 3, text: 'MWrite Test Course 1'},
            {id: 4, text: 'Auto Test Section 1'}
          ]
        },
        headings: {
          name: 'Student Name',
          section: 'Section'
        }
      },
      json_data: []
    };
  },
  computed: {
    formatData() {
      const origData = this.json_data;
      var formattedData = [];
      formattedData = origData.map(convertDataFormat);
      console.log('new data ', formattedData);

      return formattedData;
    }
  },
  methods: {
    getStudents() {
      const { courseId } = this.$store.state.userDetails;
      api.get('/course/{0}/students', courseId).then((response) => {
        console.log('response: ', response.data);
        this.json_data = response.data;
      });
    },
    customSectionFilter(row, query) {
      console.log('customSectionFilter function row: ', row);
      console.log('query: ', query);
      // need to get text corresponding to query which is the id
      return (row['section'] === query);
    }
  },
  created: function() {
    this.getStudents();
  }
};

const convertDataFormat = (rowData) => {
  var concatSections = rowData['sections'][0]['name'];
  var fullName = rowData['fullName'] + ' (' + rowData['username'] + ')';

  return {name: fullName, section: concatSections};
};
</script>

<style scoped>
table {
  font: red;
}
</style>
