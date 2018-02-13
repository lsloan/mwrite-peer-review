<template>
  <div>
    <h2>Title will go here</h2>
    <div>
      <div>
        <div>
        </div>
        <div></div>
      </div>
      <table>
        <tr>
          <td>
            <input v-model='nameFilter' placeholder='enter name'>
          </td>
          <td>
            <select v-model='selected'>
              <option value='0'>All Students</option>
              <option v-for='(option, key) in possibleSections' :value='key' :key='key'>
                {{option}}
              </option>
            </select>
            <span>Selected: {{ selected }}</span>
          </td>
        </tr>
        <tr>
          <th>Student Name</th>
          <th>Sections</th>
        </tr>
        <tr v-for='row in filteredData' :key='row.index'>
          <td>{{row.name}}</td>
          <td>
            <span v-for='(section, index) in row.section.names' :key='index'>{{section}}
              <span v-if='index < row.section.names.length -1'>,&nbsp;
              </span>
          </span>
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
      json_data: [],
      parsedData: [],
      selected: '0',
      nameFilter: ''
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
    possibleSections() {
      var allSections = this.json_data.reduce(function(acc, next) {
        var sections = next['sections'];

        for(var i = 0; i < sections.length; i++) {
          if(!acc.hasOwnProperty(sections[i]['id'])) {
            // console.log('adding section');
            acc[sections[i]['id']] = sections[i]['name'];
          }
        }

        return acc;
      }, {});
      return allSections;
    },
    filteredData() {
      var filteredData = [];
      const parsedData = this.formatData;
      console.log('section selected:', this.selected);
      console.log('name selected:', this.nameFilter);
      // should be an 'AND' filter

      if(this.selected === '0' && this.nameFilter === '') {
        console.log('NO filter');
        return parsedData;
      }

      const sectionSelected = this.selected;
      const nameSelected = this.nameFilter;

      parsedData.filter(function(row) {
        if(sectionSelected !== '0' && nameSelected !== '') {
          // both criteria selected
          // must filter by both using AND
          console.log('filter by BOTH');
          return true;
        }
        if(sectionSelected !== '0') {
          // only filter by section
          console.log('only filter by section');
        }
        if(nameSelected !== '') {
          // only filter by name.
          // match nameSelected to any substring?
          console.log('only filter by name');
        }
      });

      return filteredData;
    }
  },
  methods: {
    getStudents() {
      const { courseId } = this.$store.state.userDetails;
      api.get('/course/{0}/students', courseId).then((response) => {
        console.log('response: ', response.data);
        this.json_data = response.data;
      });
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
