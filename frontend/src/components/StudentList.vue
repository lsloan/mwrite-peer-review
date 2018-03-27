<template>
  <div class='mdl-grid'>
    <div class='mdl-cell mdl-cell--12-col'>
      <h1>{{courseName}} Students</h1>
    </div>
    <div class='mdl-cell align-with-table'>
      <mdl-select class='clickable' label='Section Filter' v-model='selected' id='section-select' :options='possibleSections'>
      </mdl-select>
    </div>
    <div class='mdl-cell align-with-table'>
      <div class='mdl-textfield flexbox'>
        <input v-model='nameFilter' class="mdl-textfield__input clickable" type="text" placeholder='Search for a student' id='name-filter'>
        <i class="material-icons" id='glass'>search</i>
      </div>
    </div>
    <div class='mdl-cell mdl-cell--12-col'>
      <table class='mdl-data-table mdl-js-data-table'>
        <thead>
          <tr class='no-top-border'>
            <th class='mdl-data-table__cell--non-numeric table-heading'>Student Name</th>
            <th class='mdl-data-table__cell--non-numeric table-heading'>Sections</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for='row in filteredData' :key='row.index'>
            <td class='mdl-data-table__cell--non-numeric clickable'>{{row.name}}</td>
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
</template>

<script>
// import api from '@/services/api';
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
    courseName() {
      return this.$store.state.userDetails.courseName;
    },
    formatData() {
      const origData = this.json_data;
      var formattedData = [];
      formattedData = origData.map(convertDataFormat);
      console.log('new data ', formattedData);
      formattedData.sort(alphabeticalSort);
      console.log('SORTED data', formattedData);
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
      this.$api.get('/course/{0}/students', courseId).then((response) => {
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

var alphabeticalSort = function(a, b) {
  if(a.name.toLowerCase() < b.name.toLowerCase()) {
    return -1;
  }
  if(a.name.toLowerCase() > b.name.toLowerCase()) {
    return 1;
  }
  return 0;
};
</script>

<style scoped>
@media (max-width: 480px) {
  .align-with-table {
    width: 100%;
  }
}

h1 {
  font-size: 30px;
  font-weight: 700;
}

table {
  width: 100%;
  border-style: solid hidden;
}

.no-top-border {
  border-top-style: hidden;
}

.table-heading {
  font-size: 18px;
  color: black;
}

td {
  font-size: 15px;
}

.align-with-table {
    padding-left: 24px;
}

.clickable:hover {
  cursor: pointer;
}

.clickable >>> input:hover {
  cursor: pointer;
}

#name-filter {
  z-index: 10;
}

#glass {
  margin-left: -30px;
}

.flexbox {
  display: flex;
}
</style>
