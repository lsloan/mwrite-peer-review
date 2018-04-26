<template>
  <div class="mdl-grid">
    <div class="mdl-cell mdl-cell--12-col">
      <h1 class="title">{{courseName}} Students</h1>
    </div>
    <div class="mdl-cell mdl-cell--3-col mdl-cell--3-col-tablet mdl-cell--4-col-phone">
      <div class="mdl-textfield">
        <dropdown id="section-select" label="Section Filter" v-model="selected" :options="possibleSections" :disabled="false">
        </dropdown>
      </div>
    </div>
    <div class="mdl-cell mdl-cell--3-col mdl-cell--3-col-tablet mdl-cell--4-col-phone">
      <div class="mdl-textfield flexbox">
        <input v-model="nameFilter" class="mdl-textfield__input clickable" type="text" placeholder="Search for a student" id="name-filter">
        <i class="material-icons" id="glass">search</i>
      </div>
    </div>
    <div class="mdl-cell mdl-cell--6-col mdl-cell--2-col-tablet mdl-cell--hide-phone"></div>
    <div class="mdl-cell mdl-cell--12-col x-scrollable">
      <table class="mdl-data-table mdl-js-data-table student-table">
        <thead>
          <tr class="no-top-border">
            <th class="mdl-data-table__cell--non-numeric table-heading">Student Name</th>
            <th class="mdl-data-table__cell--non-numeric table-heading">Sections</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="2" class="centralized student-table-cell">
              <mdl-spinner single-color></mdl-spinner>
            </td>
          </tr>
          <tr v-on:click="goToStudent(row.id)" v-for="row in filteredPaginatedData" :key="row.index">
            <td class="mdl-data-table__cell--non-numeric clickable student-table-cell">
              <a class="plain-link" :href="studentLink(row.id)">{{row.name}}</a>
            </td>
            <td class="mdl-data-table__cell--non-numeric clickable student-table-cell">
              <span v-for="(section, index) in row.section.names" :key="index">{{section}}
                <span v-if="index < row.section.names.length -1">,&nbsp;
                </span>
            </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flexbox pagination-container x-scrollable" v-if="isLoading === false">
      <button class="pagination-button" type="button" v-on:click="goToPrevPage">Prev</button>

      <div v-for="(currentButton, index) in buttonsToShow" v-bind:key="index">
        <span v-if="currentButton==='...'" class="page-gap">{{currentButton}}</span>
        <button class="pagination-button" v-else type="button" v-on:click="goToPage(currentButton)" v-bind:class="{'current-page':(currentButton == currentPage)}" :disabled="currentButton == currentPage">
          {{currentButton}}
        </button>
      </div>

      <button class="pagination-button" type="button" v-on:click="goToNextPage">Next</button>
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
      jsonData: [],
      parsedData: [],
      selected: {'value': '0', 'name': 'All Students'},
      nameFilter: '',
      rowsPerPage: 20,
      currentPage: 1,
      isLoading: true,
      numPageShow: 3,
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
      return this.jsonData
        .map(convertDataFormat)
        .sort(alphabeticalSort);
    },
    filteredData() {
      const parsedData = this.formatData;
      const sectionSelected = this.selected.value;
      const nameSelected = this.nameFilter;

      if(sectionSelected === '0' && nameSelected === '') {
        return parsedData;
      }

      return parsedData.filter(row => {
        if(sectionSelected !== '0' && nameSelected !== '') {
          const includesSection = row['section']['ids'].includes(parseInt(sectionSelected));
          const includesName = row['name'].toLowerCase().includes(nameSelected.toLowerCase());

          return includesSection && includesName;
        }
        if(sectionSelected !== '0') {
          return row['section']['ids'].includes(parseInt(sectionSelected));
        }
        if(nameSelected !== '') {
          return (row['name'].toLowerCase()).includes(nameSelected.toLowerCase());
        }
      });
    },
    filteredPaginatedData() {
      const allFilteredData = this.filteredData;
      const startIndex = this.rowsPerPage * (this.currentPage - 1);
      const endIndex = this.rowsPerPage * this.currentPage - 1;

      return allFilteredData.slice(startIndex, endIndex + 1);
    },
    lastPage() {
      return Math.ceil(this.filteredData.length / this.rowsPerPage);
    },
    possibleSections() {
      const allSections = this.jsonData.reduce((acc, next) => {
        const sections = next['sections'];

        for(let i = 0; i < sections.length; i++) {
          if(!acc.hasOwnProperty(sections[i]['id'])) {
            acc[sections[i]['id']] = sections[i]['name'];
          }
        }

        return acc;
      }, {});
      allSections[0] = 'All students';

      return Object.entries(allSections).map(([id, name]) => ({
        name: name,
        value: id
      }));
    },
    buttonsToShow() {
      let pagesArray = [];

      if(this.currentPage - this.numPageShow > 1) {
        pagesArray.push(1);
      }
      if(this.currentPage - this.numPageShow > 2) {
        pagesArray.push('...');
      }
      const blockBefore = this.customRange(this.currentPage - this.numPageShow, this.currentPage);

      pagesArray = pagesArray.concat(blockBefore);

      pagesArray.push(this.currentPage);

      const blockAfter = this.customRange(this.currentPage + 1, this.currentPage + this.numPageShow + 1);

      pagesArray = pagesArray.concat(blockAfter);

      if(this.currentPage + this.numPageShow < this.lastPage - 1) {
        pagesArray.push('...');
      }
      if(this.currentPage + this.numPageShow < this.lastPage) {
        pagesArray.push(this.lastPage);
      }

      while(pagesArray.length < (2 * this.numPageShow + 5) && this.lastPage > (2 * this.numPageShow + 5)) {
        if(pagesArray[1] === '...') {
          pagesArray.splice(2, 0, pagesArray[2] - 1);
        }
        if(pagesArray[(pagesArray.length - 2)] === '...') {
          pagesArray.splice((pagesArray.length - 2), 0, pagesArray[(pagesArray.length - 3)] + 1);
        }
      }

      return pagesArray;
    }
  },
  methods: {
    getStudents() {
      this.isLoading = true;
      const { courseId } = this.$store.state.userDetails;
      this.$api.get('/course/{0}/students', courseId).then(response => {
        this.jsonData = response.data;
        this.isLoading = false;
      });
    },
    goToNextPage() {
      if(this.currentPage < this.lastPage) {
        this.currentPage = this.currentPage + 1;
      }
    },
    goToPrevPage() {
      if(this.currentPage > 1) {
        this.currentPage = this.currentPage - 1;
      }
    },
    goToPage(pageNum) {
      if(pageNum >= 1 && pageNum <= this.lastPage) {
        this.currentPage = pageNum;
      }
    },
    customRange(startNum, endNum) {
      const range = [];
      if(startNum < 1) {
        startNum = 1;
      }
      for(let i = startNum; i < endNum; i++) {
        if(i > this.lastPage) {
          return range;
        }
        range.push(i);
      }

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
      this.currentPage = 1;
    }
  },
  created: function() {
    this.getStudents();
  }
};

const convertDataFormat = (rowData) => {
  const sectionNamesIds = rowData['sections'].reduce((acc, next) => {
    acc['names'].push(next['name']);
    acc['ids'].push(next['id']);

    return acc;
  }, {names: [], ids: []});

  const fullName = rowData['sortableName'];

  return {name: fullName, section: sectionNamesIds, id: rowData['id']};
};

const alphabeticalSort = (a, b) => {
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
.title {
  font-size: 30px;
  font-weight: 700;
}

.student-table {
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

.student-table-cell {
  font-size: 15px;
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

.pagination-button {
  cursor: pointer;
  margin: 0.75em;
  padding: 0.75em;
  min-width: 3em;
  min-height: 3em;
}

.pagination-container {
  margin: auto;
}

.pagination-button:hover {
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
  width: initial;
  padding: 10px 0;
}

.mdl-textfield__input {
  width: initial;
}

.centralized {
  text-align: center;
}

.plain-link, .plain-link:hover, .plain-link:focus {
  color: black;
  text-decoration: none;
}
</style>
