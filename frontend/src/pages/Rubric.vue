<template>
    <form id="rubric-form" @submit.prevent>
        <template v-if="reviewIsInProgress">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
                <mdl-card
                        class="read-only-rubric-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                        supporting-text="Reviews are in progress, so this rubric is now read-only."></mdl-card>
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            </div>
        </template>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>

            <!-- TODO pull this out into its own component -->
            <!-- TODO double check markup vs the below -->
            <mdl-card
                    id="prompt-card"
                    class="mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Writing Prompt"
                    supporting-text="slot">
                <div slot="supporting-text">
                    <div class="mdl-card__supporting-text">

                        <dropdown
                                id="prompt-menu"
                                label="The rubric will be applied to the following assignment:"
                                v-model="selectedPrompt"
                                :options="promptChoices"
                                :disabled="reviewIsInProgress"
                                empty-caption="Select an assignment">
                        </dropdown>
                        <p v-if="promptSection && promptDueDate" class="assignment-info">
                            This prompt is assigned to {{ promptSection }} and is due {{ promptDueDate }}.
                        </p>
                    </div>

                    <!-- TODO this could be abstracted into its own component -->
                    <div v-if="promptIssues.length > 0" class="mdl-card__supporting-text validations-container">
                        <ul class="mdl-list">
                            <li v-for="(issue, index) in promptIssues" :key="index" class="mdl-list__item">
                                <span class="mdl-list__item-primary-content">
                                    <i v-if="issue.fatal" class="material-icons mdl-list__item-icon">warning</i>
                                    <i v-else class="material-icons mdl-list__item-icon">error_outline</i>
                                    {{ issue.message }}
                                </span>
                            </li>
                        </ul>
                    </div>

                </div>
            </mdl-card>

            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>

            <mdl-card
                    class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Peer Review"
                    supporting-text="slot">
                <div slot="supporting-text">

                    <!-- TODO disabled due to lack of demand -->
                    <div v-if="false" class="mdl-card__supporting-text">
                        <mdl-switch v-model="distributePeerReviewsForSections" :disabled="reviewIsInProgress">
                            Distribute peer reviews only to students in the same section
                        </mdl-switch>
                    </div>

                    <div class="mdl-card__supporting-text">
                        <mdl-switch v-model="data.rubric.peerReviewOpenDateIsPromptDueDate" :disabled="reviewIsInProgress">
                            Use the writing prompt's due date as the peer review open date
                        </mdl-switch>
                    </div>
                    <div v-if="!peerReviewOpenDateIsPromptDueDate" class="mdl-card__supporting-text datetime-container">
                        <p>Enter a custom date:</p>
                        <div>
                            <datepicker
                                    format="MMM d yyyy"
                                    placeholder="Day"
                                    :disabled="peerReviewOpenDisabledDates"
                                    :disabled-picker="reviewIsInProgress"
                                    v-model="selectedPeerReviewOpenDate">
                            </datepicker>
                        </div>
                        <div>
                            <mdl-select
                                    id="peer-review-open-hour-select"
                                    label="Hour"
                                    v-model="peerReviewOpenHour"
                                    :disabled="reviewIsInProgress"
                                    :options="peerReviewOpenHourChoices">
                            </mdl-select>
                        </div>
                        <div>
                            <mdl-select
                                    id="peer-review-open-minute-select"
                                    label="Minute"
                                    v-model="peerReviewOpenMinute"
                                    :disabled="reviewIsInProgress"
                                    :options="peerReviewOpenMinuteChoices">
                            </mdl-select>
                        </div>
                        <div>
                            <mdl-select
                                    id="peer-review-open-ampm-select"
                                    label="AM / PM"
                                    v-model="peerReviewOpenAMPM"
                                    :disabled="reviewIsInProgress"
                                    :options="peerReviewOpenAMPMChoices">
                            </mdl-select>
                        </div>

                    </div>
                    <div class="mdl-card__supporting-text">
                        <p v-if="peerReviewOpenDateIsValid">
                            Peer reviews will be distributed at {{ peerReviewOpenDateStr }}.  Students who have
                            not completed the writing prompt assignment in Canvas by this date will be unable
                            to participate in peer review.
                        </p>
                        <p v-else-if="!peerReviewOpenDateIsPromptDueDate">
                            The peer review open date must be between the prompt assignments's due date and the peer review's due date.
                        </p>
                    </div>
                </div>
            </mdl-card>

            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>

        <template v-if="!(reviewIsInProgress && !selectedRevision.value)">
            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>

                <!-- TODO pull this out into its own component -->
                <!-- TODO double check markup vs the above -->
                <mdl-card
                        class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                        title="Revision"
                        supporting-text="slot">
                    <div slot="supporting-text">
                        <div class="mdl-card__supporting-text">
                            <dropdown
                                    id="revision-menu"
                                    label="If students will be completing a revision, please select the revision assignment here."
                                    v-model="selectedRevision"
                                    :options="revisionChoices"
                                    :disabled="reviewIsInProgress">
                            </dropdown>
                            <p v-if="revisionSection && revisionDueDate" class="assignment-info">
                                This revision is assigned to {{ revisionSection }} and is due {{ revisionDueDate }}.
                            </p>
                        </div>

                        <!-- TODO this could be abstracted into its own component -->
                        <div v-if="revisionIssues.length > 0" class="mdl-card__supporting-text validations-container">
                            <ul class="mdl-list">
                                <li v-for="(issue, index) in revisionIssues" :key="index" class="mdl-list__item">
                                    <span class="mdl-list__item-primary-content">
                                        <i v-if="issue.fatal" class="material-icons mdl-list__item-icon">warning</i>
                                        <i v-else class="material-icons mdl-list__item-icon">error_outline</i>
                                        {{ issue.message }}
                                    </span>
                                </li>
                            </ul>
                        </div>

                    </div>
                </mdl-card>

                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            </div>
        </template>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>

            <mdl-card
                    class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Description"
                    supporting-text="slot">
                <div slot="supporting-text" class="mdl-card__supporting-text">
                    <autosize-textarea v-model="rubricDescription" label="Enter a description for this rubric here." :disabled="reviewIsInProgress"></autosize-textarea>
                </div>
            </mdl-card>

            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>

        <div class="mdl-grid">
            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>

            <mdl-card
                    class="mdl-card mdl-shadow--2dp mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone"
                    title="Criteria"
                    supporting-text="slot"
                    :actions="!reviewIsInProgress ? 'slot' : ''">
                <div slot="supporting-text" class="criteria-container mdl-card__supporting-text">

                    <mdl-card v-for="(criterion, index) in criteria" :key="criterion.id" class="criterion-card mdl-shadow--2dp" supporting-text="slot">
                        <div slot="supporting-text">
                            <div v-if="!reviewIsInProgress && index > 0" class="criterion-delete-button-container">
                                <button type="button" class="mdl-chip__action" tabindex="-1" @click="removeCriterion(criterion.id)">
                                    <i class="material-icons">cancel</i>
                                </button>
                            </div>
                            <div class="mdl-card__supporting-text">
                                <autosize-textarea v-model="criterion.description" label="Enter a description for this criterion here." :disabled="reviewIsInProgress"></autosize-textarea>
                            </div>
                        </div>
                    </mdl-card>

                </div>
                <div slot="actions" class="mdl-card__actions">
                    <button type="button"
                            class="mdl-button mdl-js-button mdl-button--fab mdl-button--mini-fab mdl-button--colored"
                            @click="addCriterion">
                        <i class="material-icons">add</i>
                    </button>
                </div>
            </mdl-card>

            <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
        </div>

        <template v-if="!reviewIsInProgress">

            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
                <div class="mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone">
                    <button
                            class="mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent"
                            type="submit"
                            :disabled="!rubricIsValid || submissionInProgress"
                            @click="submitRubricForm">
                        Submit
                    </button>
                </div>
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            </div>

            <div class="mdl-grid">
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
                <div class="mdl-cell mdl-cell--10-col mdl-cell--6-col-tablet mdl-cell-2-col-phone">
                    <mdl-snackbar display-on="notification"></mdl-snackbar>
                </div>
                <div class="mdl-cell mdl-cell--1-col mdl-cell--1-col-tablet mdl-cell-1-col-phone"></div>
            </div>

        </template>
    </form>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';
import Datepicker from 'vuejs-datepicker';

import Dropdown from '@/components/Dropdown';
import AutosizeTextarea from '@/components/AutosizeTextarea';

import {gensym} from '@/services/util';
import {validationInfoAsIssues} from '@/services/validation';

const makeCriterion = (prefix = 'criterion', description = '') => {
  return {
    id: gensym(prefix),
    description: description
  };
};

const NO_REVISION_OPTION = {value: null, name: 'No revision'};
const DISPLAY_DATE_FORMAT = 'MMM D YYYY h:mm A';
const DEFAULT_CRITERIA = [makeCriterion()];

export default {
  components: {Dropdown, Datepicker, AutosizeTextarea},
  // directives: VueMdl.directives, // TODO still need this?
  props: ['peer-review-assignment-id'],
  data() {
    return {
      assignmentNamesById: {},
      existingRubric: null,
      validations: {},
      models: {
        criteria: DEFAULT_CRITERIA,
        description: '',
        peerReviewOpenDate: null,
        peerReviewOpenDateIsPromptDueDate: true,
        selectedPrompt: null,
        selectedRevision: NO_REVISION_OPTION
      },
      submissionInProgress: false,
      peerReviewOpenHourChoices: R.range(1, 13).map(i => i.toString()),
      peerReviewOpenMinuteChoices: ['00', '15', '30', '45'],
      peerReviewOpenAMPMChoices: ['AM', 'PM']
    };
  },
  computed: {
    courseId() {
      return this.$store.state.userDetails.courseId;
    },
    reviewIsInProgress() {
      const {rubric: {reviewIsInProgress = false} = {}} = this.data || {};
      return reviewIsInProgress;
    },
    promptChoices() {
      if(this.data && this.data.assignments) {
        return this.data.assignments.filter(option => {
          const selectedRevisionId = this.selectedRevision && this.selectedRevision.value;
          const selectedPromptId = this.selectedPrompt && this.selectedPrompt.value;
          return option.value !== selectedRevisionId && option.value !== selectedPromptId;
        });
      }
    },
    revisionChoices() {
      if(this.data && this.data.assignments) {
        const selectedRevisionId = this.selectedRevision && this.selectedRevision.value;
        const revisionOptions = selectedRevisionId
          ? [NO_REVISION_OPTION].concat(this.data.assignments)
          : this.assignments;
        return revisionOptions.filter(option => {
          if(typeof (option) !== 'undefined') {
            const selectedPromptId = this.selectedPrompt && this.selectedPrompt.value;
            return !option.value || (option.value !== selectedPromptId && option.value !== selectedRevisionId);
          }
        });
      }
    },
    promptIssues() {
      if(this.selectedPrompt) {
        const validations = this.data.validations[this.selectedPrompt.value];
        return validationInfoAsIssues(validations, true);
      }
      else {
        return [];
      }
    },
    revisionIssues() {
      const selectedRevisionId = this.selectedRevision.value;
      return this.selectedRevision && selectedRevisionId
        ? validationInfoAsIssues(this.data.validations[selectedRevisionId], false)
        : [];
    },
    promptSection() {
      if(this.selectedPrompt) {
        const validations = this.validations[this.selectedPrompt.value];
        return validations.sectionName || 'all students';
      }
    },
    promptDueDate() {
      if(this.selectedPrompt) {
        const validations = this.validations[this.selectedPrompt.value];
        return moment(validations.dueDateUtc).local().format(DISPLAY_DATE_FORMAT);
      }
    },
    revisionSection() {
      const selectedRevisionId = this.selectedRevision.value;
      if(this.selectedRevision && selectedRevisionId) {
        const validations = this.validations[selectedRevisionId];
        return validations.sectionName || 'all students';
      }
    },
    revisionDueDate() {
      const selectedRevisionId = this.selectedRevision.value;
      if(this.selectedRevision && selectedRevisionId) {
        const validations = this.validations[selectedRevisionId];
        return moment(validations.dueDateUtc).local().format(DISPLAY_DATE_FORMAT);
      }
    },
    rubricIsValid() {
      if(this.data && this.data.rubric) {
        const criteriaExist = !R.isEmpty(this.data.rubric.criteria);
        const criteriaDescriptionsExist = R.all(this.data.rubric.criteria, c => !R.isEmpty(c.description));
        const criteriaAreValid = criteriaExist && criteriaDescriptionsExist;

        const allIssues = R.concat(this.promptIssues, this.revisionIssues);
        const noFatalIssuesFound = R.all(allIssues, i => !i.fatal);

        return this.selectedPrompt && this.rubric.description && criteriaAreValid && noFatalIssuesFound && this.peerReviewOpenDateIsValid;
      }
    },
    peerReviewOpenDisabledDates: function() {
      var dates = {};
      if(this.promptDueDate && this.existingPeerReviewDueDate) {
        var toMoment = moment(this.promptDueDate, DISPLAY_DATE_FORMAT);
        var fromMoment = moment(this.existingPeerReviewDueDate);

        toMoment.startOf('day');
        fromMoment.startOf('day');

        dates = {
          to: toMoment.toDate(),
          from: fromMoment.toDate()
        };
      }
      return dates;
    },
    peerReviewOpenDate: function() {
      var date = null;
      if(this.peerReviewOpenDateIsPromptDueDate) {
        date = moment(this.promptDueDate, DISPLAY_DATE_FORMAT).utc().toDate();
      }
      else {
        if(this.selectedPeerReviewOpenDate && this.peerReviewOpenHour && this.peerReviewOpenMinute && this.peerReviewOpenAMPM) {
          var hours12 = parseInt(this.peerReviewOpenHour);

          var hours24 = null;
          if(this.peerReviewOpenAMPM === 'AM') {
            hours24 = hours12 === 12 ? 0 : parseInt(hours12);
          }
          else {
            hours24 = hours12 === 12 ? 12 : parseInt(hours12) + 12;
          }

          var minutes = parseInt(this.peerReviewOpenMinute);
          date = moment(this.selectedPeerReviewOpenDate)
            .hours(hours24)
            .minutes(minutes)
            .utc()
            .toDate();
        }
      }
      return date;
    },
    peerReviewOpenDateStr: function() {
      var dateStr = '';
      if(this.peerReviewOpenDate) {
        dateStr = moment(this.peerReviewOpenDate).format(DISPLAY_DATE_FORMAT);
      }
      return dateStr;
    },
    peerReviewOpenDateIsValid: function() {
      if(!this.peerReviewOpenDate) {
        return false;
      }
      var peerReviewOpenDate = moment(this.peerReviewOpenDate);
      var promptDueDate = moment(this.promptDueDate, DISPLAY_DATE_FORMAT);
      var peerReviewDueDate = moment(this.existingPeerReviewDueDate);
      return peerReviewOpenDate.isSameOrAfter(promptDueDate) && peerReviewOpenDate.isSameOrBefore(peerReviewDueDate);
    }
  },
  methods: {
    fetchData() {
      return this.$api.get('/course/{}/rubric/peer_review_assignment/{}', this.courseId, this.peerReviewAssignmentId)
        .then(r => {
          const {assignments, validations, existingRubric} = r.data;
          this.assignmentNamesById = assignments;
          this.validations = validations;
          this.existingRubric = existingRubric;
        });
    },
    initializeModels() {
      if(this.existingRubric) {
        const {promptId, revisionId} = this.existingRubric;
        const promptName = this.assignmentNamesById[promptId];
        const revisionName = this.assignmentNamesById[revisionId];
        const promptOption = {value: promptId, name: promptName};
        const revisionOption = {value: revisionId, name: revisionName};

        const modelConverter = R.pipe(
          R.dissoc('promptId'),
          R.dissoc('revisionId'),
          R.assoc('selectedPrompt', promptOption),
          R.assoc('selectedRevision', revisionOption)
        );

        this.models = modelConverter(this.existingRubric);
      }
    },
    updatePeerReviewOpenDate(newPromptDueDateLocal) {
      if(newPromptDueDateLocal) {
        const date = moment(newPromptDueDateLocal, DISPLAY_DATE_FORMAT);
        const minute = date.minute();

        // TODO the following could be replaced with _.flow(), but only if we use lodash.fp which will be much easier w/ ES6
        let closestMinuteChoice = R.pipe(
          R.filter(c => parseInt(c) >= minute),
          R.minBy(c => Math.abs(minute - parseInt(c)))
        )(this.peerReviewOpenMinuteChoices);

        if(!closestMinuteChoice) {
          const minutesToHour = 60 - minute;
          date.add(minutesToHour, 'minutes');
          closestMinuteChoice = '00';
        }

        let meridian = 'AM';
        let hour = date.hour();
        if(hour === 0) {
          hour = 12;
        }
        else {
          if(hour >= 12) {
            meridian = 'PM';
            if(hour > 12) {
              hour -= 12;
            }
          }
        }

        this.peerReviewOpenHour = hour.toString();
        this.peerReviewOpenMinute = closestMinuteChoice;
        this.peerReviewOpenAMPM = meridian;
        this.selectedPeerReviewOpenDate = date.toDate();
      }
    },
    addCriterion: function() {
      this.criteria.push(makeCriterion());
    },
    removeCriterion: function(id) {
      this.criteria = this.criteria.filter(function(criterion) {
        return criterion.id !== id;
      });
    }
    // submitRubricForm: function() {
    //   if(this.rubricIsValid) {
    //     var data = {
    //       promptId: this.selectedPrompt.value || null,
    //       revisionId: this.selectedRevision.value || null,
    //       description: this.rubric ? R.trim(this.rubric.description) : null,
    //       criteria: _.map(this.criteria, function(c) {
    //         return _.trim(c.description) || null;
    //       }),
    //       peerReviewOpenDateIsPromptDueDate: this.peerReviewOpenDateIsPromptDueDate,
    //       peerReviewOpenDate: moment(this.peerReviewOpenDate).utc().format(),
    //       distributePeerReviewsForSections: this.distributePeerReviewsForSections
    //     };

    //     this.submissionInProgress = true;
    //     var vm = this;
    //     postToEndpoint(
    //       document.querySelector('#rubric-form').getAttribute('action'),
    //       data,
    //       function() {
    //         vm.$root.$emit('notification', {
    //           message: 'The rubric was successfully created.  You will be returned to the dashboard.'
    //         });
    //         var frontendLandingUrl = document.querySelector('#rubric-form').dataset['frontendLandingUrl'];
    //         var redirectToDashboard = function() {
    //           window.location.href = frontendLandingUrl + '/#/instructor/dashboard';
    //         };
    //         setTimeout(redirectToDashboard, 4000);
    //       },
    //       function() {
    //         // TODO be more specific in certain cases e.g. 403 (session probably expired)
    //         vm.$root.$emit('notification', {
    //           message: 'An error occurred.  Please try again later.'
    //         });
    //       },
    //       function() {
    //         vm.submissionInProgress = false;
    //       }
    //     );
    //   }
    //   else {
    //     // TODO not bad to have a guard, but this should be unreachable, so we need another way to tell the user what to do / what not do
    //     this.$root.$emit('notification', {
    //       message: 'This rubric is not valid.  Double check that you have selected a writing prompt, added a description, created criteria, and configured a peer review open date no sooner than the prompt\'s open date.'
    //     });
    //   }
    // }
  },
  mounted() {
    this.fetchData().then(this.initializeModels);
  }
};
</script>

<style scoped>
    form {
        width: 100%;
        height: 100%;
    }

    .hidden {
        display: none !important;
    }

    textarea {
        resize: none;
    }

    .mdl-textfield {
        width: 100%;
    }

    .mdl-card, .mdl-card .mdl-card__supporting-text {
        overflow: visible;
        z-index: auto;
    }

    .criterion-card {
        margin-bottom: 16px;
        width: 100%;
        min-height: 0;
    }

    .criterion-delete-button-container {
        height: 0;
    }

    .criterion-delete-button-container > button.mdl-chip__action {
        float: right;
    }

    button[type="submit"] {
        display: block;
        margin: 0 auto;
    }

    #prompt-menu, #revision-menu {
        border-bottom: 1px solid darkgray;
        border-radius: 4px;
        margin-top: 20px;
        text-transform: none;
        display: block;
        min-width: 60%;
        text-align: left;
    }

    .validations-container {
        padding-top: 0;
        padding-bottom: 0;
    }

    .validations-container span {
        font-size: 14px;
    }

    .validations-container > ul {
        margin-top: 0;
        margin-bottom: 0;
    }

    .assignment-info {
        margin-top: 25px;
    }

    /* TODO still needed? */
    .read-only-rubric-card {
        min-height: 0;
    }

    /* TODO still needed? */
    .read-only-rubric-card h4 {
        margin-top: 16px;
        margin-bottom: 16px;
    }

    #rubric-form textarea[disabled], #rubric-form button[disabled][type=button] {
        color: inherit;
    }

    .vdp-datepicker input[type="text"] {
        font-size: 14px;
        padding: 1%;
        max-width: 120px;
    }

    .datetime-container > div, .datetime-container .vdp-datepicker, .datetime-container .vdp-datepicker div {
        display: inline;
    }

    .datetime-container .mdl-textfield {
        width: 80px;
        margin-left: 3px;
        margin-right: 3px;
    }
</style>
