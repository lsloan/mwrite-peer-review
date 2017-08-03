(function() {
    var noRevisionOption = {value: null, name: 'No revision'};
    var displayDateFormat = 'MMM D YYYY h:mm A';

    var updatePeerReviewOpenDate = function(newPromptDueDateLocal) {
        if(newPromptDueDateLocal) {
            var date = moment(newPromptDueDateLocal, displayDateFormat);

            var minute = date.minute();
            // TODO the following could be replaced with _.flow(), but only if we use lodash.fp which will be much easier w/ ES6
            var closestMinuteChoice = _(this.peerReviewOpenMinuteChoices)
                .filter(function (choice) {
                    return parseInt(choice) >= minute;
                })
                .minBy(function (choice) {
                    return Math.abs(minute - parseInt(choice));
                });

            if(!closestMinuteChoice) {
                var minutesToHour = 60 - minute;
                date.add(minutesToHour, 'minutes');
                closestMinuteChoice = '00';
            }

            var meridian = 'AM';
            var hour = date.hour();
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
    };

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

            this.peerReviewOpenDateIsPromptDueDate = JSON.parse(data['peerReviewOpenDateIsPromptDueDate']);
            if(!this.peerReviewOpenDateIsPromptDueDate) {
                var dateStr = moment(data['peerReviewOpenDate']).format(displayDateFormat);
                updatePeerReviewOpenDate.call(this, dateStr);
            }

            console.log('mounted');
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
            selectedPeerReviewOpenDate: null,
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
                var dueDateStr = null;
                if(this.selectedPrompt) {
                    var validations = this.validations[this.selectedPrompt.value];
                    dueDateStr = moment(validations.dueDateUtc).local().format(displayDateFormat);
                }
                return dueDateStr
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
                var dueDateStr = null;
                if(this.selectedRevision && this.selectedRevision.value) {
                    var validations = this.validations[this.selectedRevision.value];
                    dueDateStr = moment(validations.dueDateUtc).local().format(displayDateFormat);
                }
                return dueDateStr;
            },
            rubricIsValid: function() {
                var criteriaAreValid = this.criteria.length > 0 && _.every(this.criteria, function(criterion) {
                    return criterion.description.length > 0;
                });
                var noAssignmentIssuesExist = _.every(this.promptIssues.concat(this.revisionIssues), function(issue) {
                    return !issue.fatal;
                });
                return this.selectedPrompt && this.rubricDescription && criteriaAreValid && noAssignmentIssuesExist && this.peerReviewOpenDateIsValid;
            },
            peerReviewOpenDisabledDates: function() {
                var dates = {};
                if(this.promptDueDate) {
                    dates = {to: moment(this.promptDueDate, displayDateFormat).toDate()};
                }
                return dates;
            },
            peerReviewOpenDate: function() {
                var date = null;
                if(this.peerReviewOpenDateIsPromptDueDate) {
                    date = moment(this.promptDueDate, displayDateFormat).utc().toDate();
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
                    dateStr = moment(this.peerReviewOpenDate).format(displayDateFormat);
                }
                return dateStr;
            },
            peerReviewOpenDateIsValid: function() {
                if(!this.peerReviewOpenDate) {
                    return false;
                }
                var peerReviewOpenDate = moment(this.peerReviewOpenDate);
                var promptDueDate = moment(this.promptDueDate, displayDateFormat);
                return peerReviewOpenDate.isSameOrAfter(promptDueDate);
            }
        },
        //watch: {
        //    // TODO is there a better (i.e. declarative) way to do this?
        //    selectedPrompt: {
        //        immediate: true,
        //        handler: function(newPromptDueDate, oldPromptDueDate) {
        //            console.log('hello from watch');
        //            updatePeerReviewOpenDate.call(this, newPromptDueDate);
        //        }
        //    }
        //},
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
                        criteria: _.map(this.criteria, function(c) { return _.trim(c.description) || null; }),
                        peerReviewOpenDateIsPromptDueDate: this.peerReviewOpenDateIsPromptDueDate,
                        peerReviewOpenDate: moment(this.peerReviewOpenDate).utc().format()
                    };

                    this.submissionInProgress = true;
                    var vm = this;
                    postToEndpoint(
                        document.querySelector('#rubric-form').getAttribute('action'),
                        data,
                        function() {
                            vm.$root.$emit('notification', {
                                message: 'The rubric was successfully created.  You will be returned to the dashboard.'
                            });
                            setTimeout(function() { window.location.href = '/'; }, 4000);
                        },
                        function() {
                            // TODO be more specific in certain cases e.g. 403 (session probably expired)
                            vm.$root.$emit('notification', {
                                message: 'An error occurred.  Please try again later.'
                            });
                        },
                        function() {
                            vm.submissionInProgress = false;
                        }
                    );
                }
                else {
                    // TODO not bad to have a guard, but this should be unreachable, so we need another way to tell the user what to do / what not do
                    this.$root.$emit('notification', {
                        message: 'This rubric is not valid.  Double check that you have selected a writing prompt, added a description, created criteria, and configured a peer review open date no sooner than the prompt\'s open date.'
                    });
                }
            }
        }
    });
})();
