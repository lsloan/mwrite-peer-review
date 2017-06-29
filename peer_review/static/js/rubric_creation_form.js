(function() {
    var noRevisionOption = {value: null, name: 'No revision'};

    new Vue({
        el: '#vue-root',
        components: _.defaults({'autosize-textarea': AutosizeTextarea,
                                'dropdown': Dropdown},
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
                this.selectedPrompt = {value: existingPromptId, name: this.assignments[existingPromptId]};
            }

            var existingRevisionId = parseInt(data['existingRevisionId']);
            if(existingRevisionId) {
                this.selectedRevision = {value: existingRevisionId, name: this.assignments[existingRevisionId]};
            }

            this.reviewIsInProgress = JSON.parse(data['reviewIsInProgress']);
            this.rubricDescription = data['existingRubricDescription'];
            if(data['existingCriteria']) {
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
            criteria: [{id: _.uniqueId('criterion'), description: ''}]
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
            promptInfo: function() {
                if(!this.selectedPrompt) {
                    return '';
                }
                var validations = this.validations[this.selectedPrompt.value];
                var sectionName = validations.sectionName || 'all students';
                var localDueDate = validations.localDueDate;
                if(sectionName !== null && localDueDate !== null) {
                    return 'This prompt is assigned to ' + sectionName + ' and is due ' + localDueDate + '.';
                }
                else {
                    return '';
                }
            },
            revisionInfo: function() {
                if(!this.selectedRevision || this.selectedRevision.value === null) {
                    return '';
                }
                var validations = this.validations[this.selectedRevision.value];
                var sectionName = validations.sectionName || 'all students';
                var localDueDate = validations.localDueDate;
                if(sectionName !== null && localDueDate !== null) {
                    return 'This revision is assigned to ' + sectionName + ' and is due ' + localDueDate + '.';
                }
                else {
                    return '';
                }
            },
            rubricIsValid: function() {
                var criteriaAreValid = this.criteria.length > 0 && _.every(this.criteria, function(criterion) {
                    return criterion.description.length > 0;
                });
                var noAssignmentIssuesExist = _.every(this.promptIssues.concat(this.revisionIssues), function(issue) {
                    return !issue.fatal;
                });
                return this.selectedPrompt && this.rubricDescription &&  criteriaAreValid && noAssignmentIssuesExist;
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
                        }
                    );
                }
            }
        }
    });
})();
