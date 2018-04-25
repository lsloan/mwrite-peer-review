<template>
  <div class='mdl-grid'>
    <div class='mdl-cell mdl-cell--12-col'>
      <h1>{{courseName}} Students</h1>
    </div>
    <div class='mdl-cell mdl-cell--6-col mdl-cell--4-col-tablet mdl-cell--4-col-phone'>
      <!--<mdl-select class='clickable' label='Section Filter' v-model='selected' id='section-select' :options='possibleSections'>
      </mdl-select> !-->
      <div class='mdl-textfield'>
        <dropdown id='section-select' label='Section Filter' v-model='selected' :options='possibleSections' :disabled='false'>
        </dropdown>
      </div>
    </div>
    <div class='mdl-cell mdl-cell--6-col mdl-cell--4-col-tablet mdl-cell--4-col-phone'>
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
            <td colspan='2' class='centralized'>
              <mdl-spinner single-color></mdl-spinner>
            </td>
          </tr>
          <tr v-on:click='goToStudent(row.id)' v-for='row in filteredPaginatedData' :key='row.index'>
            <td class='mdl-data-table__cell--non-numeric clickable'>
              <a class='plain-link' :href='studentLink(row.id)'>{{row.name}}</a>
            </td>
            <td class='mdl-data-table__cell--non-numeric clickable'>
              <span v-for='(section, index) in row.section.names' :key='index'>{{section}}
                <span v-if='index < row.section.names.length -1'>,&nbsp;
                </span>
            </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class='flexbox pagination-container' v-if='is_loading === false'>
      <button type='button' v-on:click='goToPrevPage'>Prev</button>

      <div v-for='(currentButton, index) in buttonsToShow' v-bind:key='index'>
        <span v-if='currentButton==="..."' class='page-gap'>{{currentButton}}</span>
        <button v-else type='button' v-on:click='goToPage(currentButton)' v-bind:class='{"current-page":(currentButton == current_page)}' :disabled='currentButton == current_page'>
          {{currentButton}}
        </button>
      </div>

      <button type='button' v-on:click='goToNextPage'>Next</button>
    </div>
  </div>
</template>

<script>
import VueMdl from 'vue-mdl';
import Vue from 'vue';
import Dropdown from '@/components/Dropdown';
Vue.use(VueMdl);

export default {
  name: 'StudentList',
  data() {
    return {
      json_data: [],
      parsedData: [],
      selected: {'value': '0', 'name': 'All Students'},
      nameFilter: '',
      rows_per_page: 20,
      current_page: 1,
      is_loading: true,
      num_page_show: 3,
      apiUrl: __API_URL__
    };
  },
  components: {
    Dropdown
  },
  computed: {
    courseName() {
      return this.$store.state.userDetails.courseName;
    },
    courseId() {
      return this.$store.state.userDetails.courseId;
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

      console.log('FILTER: ', this.selected);

      const sectionSelected = this.selected.value;
      const nameSelected = this.nameFilter;

      if(sectionSelected === '0' && nameSelected === '') {
        return parsedData;
      }

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
    },
    buttonsToShow() {
      var pagesArray = [];

      if(this.current_page - this.num_page_show > 1) {
        pagesArray.push(1);
      }
      if(this.current_page - this.num_page_show > 2) {
        pagesArray.push('...');
      }
      var blockBefore = this.customRange(this.current_page - this.num_page_show, this.current_page);

      pagesArray = pagesArray.concat(blockBefore);

      pagesArray.push(this.current_page);

      var blockAfter = this.customRange(this.current_page + 1, this.current_page + this.num_page_show + 1);

      pagesArray = pagesArray.concat(blockAfter);

      if(this.current_page + this.num_page_show < this.lastPage - 1) {
        pagesArray.push('...');
      }
      if(this.current_page + this.num_page_show < this.lastPage) {
        pagesArray.push(this.lastPage);
      }

      while(pagesArray.length < (2 * this.num_page_show + 5) && this.lastPage > (2 * this.num_page_show + 5)) {
        console.log('in while loop buttons');
        // fill up to get 11 boxes
        if(pagesArray[1] === '...') {
          // this means the current page is too close to the last page
          pagesArray.splice(2, 0, pagesArray[2] - 1);
        }
        if(pagesArray[(pagesArray.length - 2)] === '...') {
          // this means the current page is too close to the 1st page
          pagesArray.splice((pagesArray.length - 2), 0, pagesArray[(pagesArray.length - 3)] + 1);
        }
      }

      return pagesArray;
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
    },
    customRange(startNum, endNum) {
      var range = [];
      for(var i = startNum; i < endNum; i++) {
        if(i < 1) {
          continue;
        }
        if(i > this.lastPage) {
          return range;
        }
        range.push(i);
      }
      // var startNum = this.current_page - this.num_page_show
      // for(var i = ; i < this.current_page)

      return range;
    },
    studentLink(studentId) {
      return `${this.apiUrl}/course/${this.courseId}/review/student/${studentId}`;
    },
    goToStudent(studentId) {
      window.location = this.studentLink(studentId);
    }
  },
  watch: {
    filteredData() {
      // reset current page
      this.current_page = 1;
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

  return {name: fullName, section: sectionNamesIds, id: rowData['id']};
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

.pagination-container button {
  margin: 0.75em;
  padding: 0.75em;
  min-width: 3em;
  min-height: 3em;
}

.pagination-container {
  margin: auto;
}

.pagination-container button:hover {
  background-color: lightgray;
}

button.current-page {
  background-color: lightgray;
  color: black;
}

button.current-page:hover {
  color: black;
  cursor: text;
}

.page-gap {
  cursor: text;
  display: inline-block;
  margin: auto;
  padding: 0.75em;
  text-align: center;
  vertical-align: text-top;
}

.mdl-textfield {
  height: 100%;
}

.centralized {
  text-align: center;
}

.plain-link, .plain-link:hover, .plain-link:focus {
  color: black;
  text-decoration: none;
}

@media screen and (max-width: 480px) {
  .align-with-table {
    width: 100%;
    padding-left: 0px;
  }

  /*.mdl-textfield {
    width: 100%;
    min-width: 200px;
    height: 100%;
  }*/
}
</style>
