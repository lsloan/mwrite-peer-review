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
        <input v-model='nameFilter' class='mdl-textfield__input clickable' type='text' placeholder='Search for a student' id='name-filter'>
        <i class='material-icons' id='glass'>search</i>
      </div>
    </div>
    <div class='mdl-cell mdl-cell--12-col x-scrollable'>
      <table class='mdl-data-table mdl-js-data-table'>
        <thead>
          <tr class='no-top-border'>
            <th class='mdl-data-table__cell--non-numeric table-heading'>Student Name</th>
            <th class='mdl-data-table__cell--non-numeric table-heading'>Sections</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if='is_loading'>
            <td colspan='2'>
              Loading... Please wait
            </td>
          </tr>
          <tr v-for='row in filteredPaginatedData' :key='row.index'>
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
    <div>DEBUG: current page: {{current_page}}, last page: {{lastPage}}</div>
    <div class='flexbox pagination-container' v-if='is_loading === false'>
      <button type='button' v-on:click='goToPrevPage'>Prev</button>
      <button type='button' v-if='(current_page !== 1)' v-on:click='goToPage(1)'>1</button>
      <div v-if='(current_page > 3)'>...</div>
      <button type='button' v-if='(current_page !== 1 && current_page !== 2)' v-on:click='goToPage(current_page - 1)'>
        {{current_page - 1}}
      </button>
      <button type='button' class='current-page' >
        {{current_page}}
      </button>
      <button type='button' v-if='(current_page !== lastPage && current_page !== (lastPage-1))' v-on:click='goToPage(current_page + 1)'>
        {{current_page + 1}}
      </button>
      <div type='button' v-if='(current_page < lastPage - 2)'>...</div>
      <button type='button' v-if='(lastPage != 1 && current_page != lastPage)' v-on:click='goToPage(lastPage)'>
        {{lastPage}}
      </button>
      <button type='button' v-on:click='goToNextPage'>Next</button>
    </div>
  </div>
</template>

<script>
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
      nameFilter: '',
      rows_per_page: 5,
      current_page: 1,
      is_loading: true
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
      // should be an 'AND' filter
      var filteredData = [];
      const parsedData = this.formatData;

      if(this.selected === '0' && this.nameFilter === '') {
        return parsedData;
      }

      const sectionSelected = this.selected;
      const nameSelected = this.nameFilter;

      filteredData = parsedData.filter(function(row) {
        if(sectionSelected !== '0' && nameSelected !== '') {
          // both criteria selected
          // must filter by both using AND
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
    filteredPaginatedData() {
      const allFilteredData = this.filteredData;

      var startIndex = this.rows_per_page * (this.current_page - 1);
      var endIndex = this.rows_per_page * this.current_page - 1;
      // returns data to be displayed in current page
      // if endIndex is past the end of allFilteredData, javascript's slice treats it as up to end of array
      return allFilteredData.slice(startIndex, endIndex + 1);
    },
    lastPage() {
      return Math.ceil(this.filteredData.length / this.rows_per_page);
    },
    possibleSections() {
      var allSections = this.json_data.reduce(function(acc, next) {
        var sections = next['sections'];

        for(var i = 0; i < sections.length; i++) {
          if(!acc.hasOwnProperty(sections[i]['id'])) {
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
      this.is_loading = true;
      const { courseId } = this.$store.state.userDetails;
      this.$api.get('/course/{0}/students', courseId).then((response) => {
        console.log('response: ', response.data);
        this.json_data = response.data;
        this.is_loading = false;
      });
    },
    goToNextPage() {
      if(this.current_page < this.lastPage) {
        this.current_page = this.current_page + 1;
      }
    },
    goToPrevPage() {
      if(this.current_page > 1) {
        this.current_page = this.current_page - 1;
      }
    },
    goToPage(pageNum) {
      if(pageNum >= 1 && pageNum <= this.lastPage) {
        this.current_page = pageNum;
      }
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

const alphabeticalSort = function(a, b) {
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

.x-scrollable {
  overflow-x: scroll;
}

button {
  cursor: pointer;
}

.pagination-container > button {
  margin: 5px;
  padding: 5px;
  min-width: 10px;
  min-height: 10px;
}

.pagination-container > button:hover {
  color: red;
}

.current-page {
  background-color: gray;
}

@media screen and (max-width: 480px) {
  .align-with-table {
    width: 100%;
    padding-left: 0px;
  }

  .mdl-textfield {
    width: 100%;
    min-width: 200px;
  }
}
</style>
