<template>
    <div></div>
</template>

<script>
import * as R from 'ramda';
import moment from 'moment';
import Datepicker from 'vuejs-datepicker';

import Dropdown from '@/components/Dropdown';
import AutosizeTextarea from '@/components/AutosizeTextarea';

import {gensym} from '@/services/util';
import {validationInfoAsIssues} from '@/services/validation';

const NO_REVISION_OPTION = {value: null, name: 'No revision'};
const DISPLAY_DATE_FORMAT = 'MMM D YYYY h:mm A';

export default {
  components: {Dropdown, Datepicker, AutosizeTextarea},
  // directives: VueMdl.directives, // TODO still need this?
  props: ['peer-review-assignment-id'],
  data() {
    return {
      data: null,
      selectedPrompt: null,
      selectedRevision: NO_REVISION_OPTION,
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
      const selectedPromptId = this.selectedPrompt.value;
      return this.selectedPrompt && selectedPromptId
        ? validationInfoAsIssues(this.data.validations[selectedPromptId], true)
        : [];
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
      this.$api.get('/course/{}/rubric/peer_review_assignment/{}', this.courseId, this.peerReviewAssignmentId)
        .then(r => {
          this.data = r.data;
        });
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
      this.criteria.push({id: gensym('criterion'), description: ''});
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
    this.fetchData();
  }
};
</script>

<style scoped>
</style>
