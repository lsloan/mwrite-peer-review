<template>
  <div>
    <h2>Title will go here</h2>
    <div>
      <div>
        <div></div>
        <div></div>
      </div>
      <table>
        <tr>
          <th>Student Name</th>
          <th>Sections</th>
        </tr>
        <tr v-for='row in formatData' :key='row.index'>
          <td>{{row.name}}</td>
          <td v-for='(section, index) in row.section.names' :key='index'>
            <span>{{section}}</span><span v-if='index < row.section.names.length -1'>,&nbsp;</span>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'StudentList',
  data() {
    return {
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
