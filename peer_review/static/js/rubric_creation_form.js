(function() {
    var noRevisionOption = {value: null, name: 'No revision'};

    new Vue({
        el: '#vue-root',
        components: _.defaults({'autosize-textarea': AutosizeTextarea,
                                'dropdown': Dropdown,
                                'datepicker': Datepicker},
                               VueMdl.components),
        directives: VueMdl.directives,
        mounted: function() {
            var data = document.querySelector('#rubric-form').dataset;
            this.assignments = _.map(JSON.parse(data['assignments']), function(value, key) {
                return {value: parseInt(key), name: value};
            });
            this.validations = JSON.parse(data['validationInfo']);

            var existingPromptId = parseInt(data['existingPromptId']);
            if(existingPromptId) {
                this.selectedPrompt = {
                    value: existingPromptId,
                    name: _.find(this.assignments, function(a) { return a.value === existingPromptId; }).name
                };
            }

            var existingRevisionId = parseInt(data['existingRevisionId']);
            if(existingRevisionId) {
                this.selectedRevision = {
                    value: existingRevisionId,
                    name: _.find(this.assignments, function(a) { return a.value === existingRevisionId; }).name
                };
            }

            this.reviewIsInProgress = JSON.parse(data['reviewIsInProgress']);
            this.rubricDescription = data['existingRubricDescription'];

            var existingCriteria = JSON.parse(data['existingCriteria']);
            if(existingCriteria && existingCriteria.length > 0) {
                this.criteria = _.map(JSON.parse(data['existingCriteria']), function(c) {
                    return {id: _.uniqueId('criterion'), description: c};
                });
            }
        },
        data: {
            assignments: null,
            validations: null,
            reviewIsInProgress: null,
            selectedPrompt: null,
            selectedRevision: noRevisionOption,
            rubricDescription: null,
            criteria: [{id: _.uniqueId('criterion'), description: ''}],
            submissionInProgress: false,
            peerReviewOpenDateIsPromptDueDate: true,
            peerReviewOpenHourChoices: _.map(_.range(1, 13), function(i) { return i.toString(); }),
            peerReviewOpenMinuteChoices: ['00', '15', '30', '45'],
            peerReviewOpenAMPMChoices: ['AM', 'PM'],
            peerReviewOpenHour: null,
            peerReviewOpenMinute: null,
            peerReviewOpenAMPM: null
        },
        computed: {
            promptChoices: function() {
                if(!this.assignments) {
                    return null;
                }

                var vm = this;
                return _.filter(this.assignments, function(option) {
                    return option.value !== (vm.selectedRevision && vm.selectedRevision.value) && option.value !== (vm.selectedPrompt && vm.selectedPrompt.value);
                });
            },
            revisionChoices: function() {
                if(!this.assignments) {
                    return null;
                }

                var vm = this;
                var revisionSelected = this.selectedRevision && this.selectedRevision.value;
                var revisionOptions = revisionSelected ? [noRevisionOption].concat(this.assignments) : this.assignments;
                return _.filter(revisionOptions, function(option) {
                    if(typeof(option) !== 'undefined') {
                        return !option.value || (option.value !== (vm.selectedPrompt && vm.selectedPrompt.value) && option.value !== (vm.selectedRevision && vm.selectedRevision.value));
                    }
                });
            },
            promptIssues: function() {
                return this.selectedPrompt ? getValidationIssues(true, this.validations[this.selectedPrompt.value]) : [];
            },
            revisionIssues: function() {
                return this.selectedRevision && this.selectedRevision.value ? getValidationIssues(false, this.validations[this.selectedRevision.value]) : [];
            },
            promptSection: function() {
                var sectionName = null;
                if(this.selectedPrompt) {
                    var validations = this.validations[this.selectedPrompt.value];
                    sectionName = validations.sectionName || 'all students';
                }
                return sectionName
            },
            promptDueDate: function() {
                var localDueDate = null;
                if(this.selectedPrompt) {
                    var validations = this.validations[this.selectedPrompt.value];
                    localDueDate = validations.localDueDate;
                }
                return localDueDate;
            },
            revisionSection: function() {
                var sectionName = null;
                if(this.selectedRevision && this.selectedRevision.value) {
                    var validations = this.validations[this.selectedRevision.value];
                    sectionName = validations.sectionName || 'all students';
                }
                return sectionName;
            },
            revisionDueDate: function() {
                var localDueDate = null;
                if(this.selectedRevision && this.selectedRevision.value) {
                    var validations = this.validations[this.selectedRevision.value];
                    localDueDate = validations.localDueDate;
                }
                return localDueDate;
            },
            rubricIsValid: function() {
                var criteriaAreValid = this.criteria.length > 0 && _.every(this.criteria, function(criterion) {
                    return criterion.description.length > 0;
                });
                var noAssignmentIssuesExist = _.every(this.promptIssues.concat(this.revisionIssues), function(issue) {
                    return !issue.fatal;
                });
                return this.selectedPrompt && this.rubricDescription &&  criteriaAreValid && noAssignmentIssuesExist;
            },
            peerReviewOpenDisabledDates: function() {
                if(this.promptDueDate) {
                    return {
                        to: moment(this.promptDueDate, 'MMM D h:mm A').toDate()
                    };
                }
                else {
                    return {};
                }
            }
        },
        methods: {
            addCriterion: function() {
                this.criteria.push({id: _.uniqueId('criterion'), description: ''});
            },
            removeCriterion: function(id) {
                this.criteria = this.criteria.filter(function(criterion) {
                    return criterion.id !== id;
                });
            },
            submitRubricForm: function() {
                if(this.rubricIsValid) {

                    var data = {
                        promptId: this.selectedPrompt.value || null,
                        revisionId: this.selectedRevision.value || null,
                        description: _.trim(this.rubricDescription) || null,
                        criteria: _.map(this.criteria, function(c) { return _.trim(c.description) || null; })
                    };

                    this.submissionInProgress = true;
                    var vm = this;
                    postToEndpoint(
                        document.querySelector('#rubric-form').getAttribute('action'),
                        data,
                        function() {
                            vm.$root.$emit('rubricSubmitted', {
                                message: 'The rubric was successfully created.  You will be returned to the dashboard.'
                            });
                            setTimeout(function() { window.location.href = '/'; }, 4000);
                        },
                        function() {
                            vm.$root.$emit('rubricSubmitted', {
                                message: 'An error occurred.  Please try again later.'
                            });
                        },
                        function() {
                            vm.submissionInProgress = false;
                        }
                    );
                }
                else {
                    this.$root.$emit('rubricSubmitted', 'This rubric is not valid.  Double check that you have selected a writing prompt, added a description, and created criteria.');
                }
            }
        }
    });
})();
