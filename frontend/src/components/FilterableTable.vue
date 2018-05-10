<template>
    <div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--12-col">
                <h1 class="title">{{ tableName }} Students</h1>
            </div>
        </div>
        <div class="mdl-grid">
            <div v-for="{key, filter: {type, makeFilterChoices}} in filterableColumns"
                 :key="key"
                 class="mdl-cell mdl-cell--3-col mdl-cell--3-col-tablet mdl-cell--4-col-phone">
                <div v-if="type === 'absolute'"
                     class="mdl-textfield">
                    <div class="mdl-textfield flexbox">
                        <input v-model="filterValues[key]"
                               class="mdl-textfield__input clickable absolute-filter"
                               type="text"
                               placeholder="Search for a student">
                        <i class="material-icons filter-icon">search</i>
                    </div>
                </div>
                <div v-else-if="type === 'choices'"
                     class="mdl-textfield">
                    <dropdown
                        :id="key"
                        label="Section Filter"
                        v-model="filterValues[key]"
                        :options="makeFilterChoices(entries)"
                        :disabled="false"/>
                </div>
            </div>
            <div class="mdl-cell mdl-cell--6-col mdl-cell--2-col-tablet mdl-cell--hide-phone"></div>
        </div>
        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--12-col x-scrollable">
                <table class="mdl-data-table mdl-js-data-table student-table">
                    <thead>
                        <tr class="no-top-border">
                            <th v-for="{key, description} in columnMapping"
                                :key="key"
                                class="mdl-data-table__cell--non-numeric table-heading">
                                {{ description }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-if="isLoading">
                            <td colspan="2" class="centralized student-table-cell">
                                <mdl-spinner single-color></mdl-spinner>
                            </td>
                        </tr>
                        <tr v-else v-on:click="rowClickHandler(row.id)" v-for="row in paginatedFilteredEntries" :key="row.index">
                            <td v-for="{key, transform} in columnMapping"
                                :key="key"
                                class="mdl-data-table__cell--non-numeric clickable student-table-cell">
                                {{ transform(row[key]) }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="flexbox pagination-container x-scrollable" v-if="isLoading === false">
                <button class="pagination-button" type="button" v-on:click="goToPrevPage">Prev</button>

                <div v-for="(currentButton, index) in buttonsToShow" v-bind:key="index">
                    <span v-if="currentButton==='...'" class="page-gap">{{currentButton}}</span>
                    <button class="pagination-button" v-else type="button" v-on:click="goToPage(currentButton)"
                            v-bind:class="{'current-page': currentButton === currentPage}"
                            :disabled="currentButton === currentPage">
                        {{currentButton}}
                    </button>
                </div>

                <button class="pagination-button" type="button" v-on:click="goToNextPage">Next</button>
            </div>
        </div>
    </div>
</template>

<script>
import * as R from 'ramda';
import {MdlSpinner} from 'vue-mdl';
import Dropdown from '@/components/Dropdown';

export default {
  name: 'FilterableTable',
  props: [
    'table-name',
    'entries',
    'is-loading',
    'column-mapping',
    'row-click-handler',
    'make-row-link',
    'section-filter-session-storage-key'
  ],
  components: {MdlSpinner, Dropdown},
  data() {
    return {
      rowsPerPage: 20,
      currentPage: 1,
      numPageShow: 3,
      filterValues: null
    };
  },
  computed: {
    filterableColumns() {
      const filterableColumns = this.columnMapping.filter(({filter = null}) => filter);
      return filterableColumns.reverse();
    },
    filterPredicate() {
      const predicates = this.filterableColumns.map(c => {
        const filterValue = this.filterValues[c.key];
        return R.partial(c.filter.predicate, [filterValue]);
      });
      return R.allPass(predicates);
    },
    filteredEntries() {
      return R.filter(this.filterPredicate, this.entries);
    },
    paginatedFilteredEntries() {
      const allFilteredData = this.filteredEntries;
      const startIndex = this.rowsPerPage * (this.currentPage - 1);
      const endIndex = this.rowsPerPage * this.currentPage - 1;
      return allFilteredData.slice(startIndex, endIndex + 1);
    },
    lastPage() {
      return Math.ceil(this.filteredEntries.length / this.rowsPerPage);
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
    restoreSavedFilters() {
      const selectedSection = JSON.parse(sessionStorage.getItem(this.sectionFilterSessionStorageKey));
      if(selectedSection) {
        this.selectedSection = selectedSection;
      }
    },
    initializeFilterValues() {
      this.filterValues = this.filterableColumns.reduce((acc, next) => {
        acc[next.key] = next.filter.defaultValue;
        return acc;
      }, {});
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
    }
  },
  watch: {
    filteredEntries() {
      this.currentPage = 1;
    }
    // selectedSection() {
    //   window.sessionStorage.setItem(
    //     this.sectionFilterSessionStorageKey,
    //     JSON.stringify(this.selectedSection)
    //   );
    // }
  },
  mounted() {
    this.restoreSavedFilters();
    this.initializeFilterValues();
  }
};
</script>

<style scoped>
    .title {
        font-size: 30px;
        font-weight: 700;
    }

    .flexbox {
        display: flex;
    }

    .clickable:hover {
        cursor: pointer;
    }

    .clickable >>> input:hover {
        cursor: pointer;
    }

    .absolute-filter {
        z-index: 10;
    }

    .filter-icon {
        margin-left: -30px;
    }

    .x-scrollable {
        overflow-x: scroll;
    }

    .student-table {
        width: 100%;
        border-style: solid hidden;
    }

    .student-table-cell {
        font-size: 15px;
    }

    .no-top-border {
        border-top-style: hidden;
    }

    .table-heading {
        font-size: 18px;
        color: black;
    }

    .centralized {
        text-align: center;
    }

    .plain-link, .plain-link:hover, .plain-link:focus {
        color: black;
        text-decoration: none;
    }

    .pagination-button {
        cursor: pointer;
        margin: 0.75em;
        padding: 0.75em;
        min-width: 3em;
        min-height: 3em;
    }

    .pagination-button:hover {
        background-color: lightgray;
    }

    .pagination-container {
        margin: auto;
    }

    .page-gap {
        cursor: text;
        display: inline-block;
        margin: auto;
        padding: 0.75em;
        text-align: center;
        vertical-align: text-top;
    }
</style>
