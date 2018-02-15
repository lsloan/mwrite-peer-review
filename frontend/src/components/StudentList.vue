<template>
  <div class='mdl-grid'>
    <div class='mdl-cell mdl-cell--12-col'>
      <h2>Title will go here</h2>
      <div>
        <div>
          <div>
          </div>
          <div></div>
        </div>
        <table class='mdl-data-table mdl-js-data-table'>
          <thead>
          <tr>
            <td class='mdl-data-table__cell--non-numeric'>
              <input v-model='nameFilter' placeholder='enter name'>
            </td>
            <td class='mdl-data-table__cell--non-numeric'>
              <mdl-select label='Section Filter' v-model='selected' id='section-select' :options='possibleSections'>
              </mdl-select>
            </td>
          </tr>
            <tr>
              <th class='mdl-data-table__cell--non-numeric'>Student Name</th>
              <th class='mdl-data-table__cell--non-numeric'>Sections</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for='row in filteredData' :key='row.index'>
              <td class='mdl-data-table__cell--non-numeric'>{{row.name}}</td>
              <td class='mdl-data-table__cell--non-numeric'>
                <span v-for='(section, index) in row.section.names' :key='index'>{{section}}
                  <span v-if='index < row.section.names.length -1'>,&nbsp;
                  </span>
              </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import VueMdl from 'vue-mdl';
import Vue from 'vue';
Vue.use(VueMdl);

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

      filteredData = parsedData.filter(function(row) {
        if(sectionSelected !== '0' && nameSelected !== '') {
          // both criteria selected
          // must filter by both using AND
          console.log('filter by BOTH');
          return (row['section']['ids'].includes(parseInt(sectionSelected)) && (row['name'].toLowerCase()).includes(nameSelected.toLowerCase()));
        }
        if(sectionSelected !== '0') {
          // only filter by section
          return row['section']['ids'].includes(parseInt(sectionSelected));
        }
        if(nameSelected !== '') {
          // only filter by name.
          // match nameSelected to any substring?
          return (row['name'].toLowerCase()).includes(nameSelected.toLowerCase());
        }
      });

      return filteredData;
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
      allSections[0] = 'All students';
      console.log('possibleSections:', allSections);
      var sectionsList = [];

      Object.keys(allSections).forEach(function(key) {
        sectionsList.push({'name': allSections[key], 'value': key});
      });

      console.log('sectionsList:', sectionsList);
      return sectionsList;
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

  var fullName = rowData['sortableName'] + ' (' + rowData['username'] + ')';

  return {name: fullName, section: sectionNamesIds};
};
</script>

<style scoped>
table {
  width: 100%;
  border-style: solid hidden;
}
</style>
