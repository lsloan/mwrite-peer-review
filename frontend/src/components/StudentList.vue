<template>
  <div>
    <h2>Title will go here</h2>
    <div>
      <div>
        <div></div>
        <div></div>
      </div>
      <v-client-table name='studentTable' :data='formatData' :columns='cols' :options='options' >
        <span slot='section' slot-scope='props'>{{joinCommas(props.row)}}
        </span>
      </v-client-table>
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
          callback: function(row, query) {
            // console.log('triggering custom filter, this: ', this);
            // // console.log('return val of customSectionFilter:', this.customSectionFilter(row, query));
            // console.log('customSectionFilter function row: ', row['section']['ids']);
            // console.log('query: ', parseInt(query), typeof (parseInt(query)));
            // console.log('typeof elem in array:', typeof (row['section']['ids'][0]));
            // // return (row['section']['ids'].includes(parseInt(query)));
            // console.log(Boolean(row['section']['ids'].find(elem => {
            //   return (parseInt(query) === elem);
            // })));
            // const result = Boolean(row['section']['ids'].find(elem => {
            //   console.log('query in find:', query);
            //   return (parseInt(query) === elem);
            // }));
            // return result;
            return false;
          }
        }],
        listColumns: {
          section: [
            {id: 107, text: 'MWrite Test Course 1'},
            {id: 108, text: 'Section 1'},
            {id: 109, text: 'Section 2'},
            {id: 129, text: 'Auto Test Section 1'}
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
    },
    sectionOptions() {
      const origData = this.json_data;
      // var sectionIdDict = {};
      // var sectionOptions = [];
      console.log('orig', origData);
      return true;
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
    joinCommas(row) {
      console.log('the input:', row);
      return row['section']['names'].join(',');
    }
  },
  created: function() {
    this.getStudents();
  }
};

const convertDataFormat = (rowData) => {
  var sectionNamesIds = rowData['sections'].reduce(function(acc, next) {
    acc['names'].push(next['name']);
    acc['ids'].push(next['id']);

    return acc;
  }, {names: [], ids: []});

  var fullName = rowData['fullName'] + ' (' + rowData['username'] + ')';

  return {name: fullName, section: sectionNamesIds};
};
</script>

<style scoped>
table {
  font: red;
}
</style>
