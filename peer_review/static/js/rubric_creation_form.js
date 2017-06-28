(function() {
    new Vue({
        el: '#vue-root',
        components: _.defaults({'autosize-textarea': AutosizeTextarea}, VueMdl.components),
        directives: VueMdl.directives,
        mounted: function() {
            var data = _.mapValues(document.querySelector('#rubric-form').dataset, JSON.parse);
            this.assignments = data['assignments'];
            this.validations = data['validation-info'];
            this.selectedPromptId = data['existing-prompt-id'];
            this.selectedRevisionId = data['existing-revision-id'];
            this.reviewIsInProgress = data['review-is-in-progress'];
            this.rubricDescription = data['existing-rubric-description'];
            // TODO grab existing criteria
        },
        data: {
            assignments: null,
            validations: null,
            reviewIsInProgress: null,
            selectedPromptId: null,
            selectedRevisionId: null,
            rubricDescription: null,
            criteria: [{id: _.uniqueId('criterion'), description: ''}]
        },
        computed: {
            promptChoices: function() {
                if(!this.assignments) {
                    return null;
                }

                var self = this;
                return _.filter(this.assignments, function(option) {
                    return option.value !== self.selectedRevisionId && option.value !== self.selectedPromptId;
                });
            },
            revisionChoices: function() {
                if(!this.assignments) {
                    return null;
                }

                var self = this;
                var noRevisionOption = {value: null, name: 'No revision'};
                var revisionOptions = [noRevisionOption].concat(this.assignments);
                return _.filter(revisionOptions, function(option) {
                    if(typeof(option) !== 'undefined') {
                        return !option.value || (option.value !== self.selectedPromptId && option.value !== self.selectedRevisionId);
                    }
                });
            },
            promptIssues: function() {
                return this.selectedPromptId ? getValidationIssues(true, this.validations[this.selectedPromptId]) : [];
            },
            revisionIssues: function() {
                return this.selectedRevisionId ? getValidationIssues(false, this.validations[this.selectedRevisionId]) : [];
            },
            promptInfo: function() {
                if(!this.selectedPromptId) {
                    return '';
                }
                var validations = this.validations[this.selectedPromptId];
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
                if(!this.selectedRevisionId) {
                    return '';
                }
                var validations = this.validations[this.selectedRevisionId];
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
                return this.selectedPromptId && this.rubricDescription &&  criteriaAreValid && noAssignmentIssuesExist;
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
                        promptId: this.selectedPromptId || null,
                        revisionId: this.selectedRevisionId || null,
                        description: _.trim(this.rubricDescription) || null,
                        criteria: _.map(this.criteria, function(c) { return _.trim(c.description) || null; })
                    };

                    postToEndpoint(
                        document.querySelector('#rubric-form').getAttribute('action'), // TODO eventually we'll want to bring this under VueJS's control as well
                        data,
                        function() {
                            // TODO is there a better event source than $root?
                            this.$root.$emit('rubricSubmitted', {
                                message: 'The rubric was successfully created.  You will be returned to the dashboard.'
                            });
                            setTimeout(function() { window.location.href = '/'; }, 4000);
                        },
                        function() {
                            // TODO is there a better event source than $root?
                            this.$root.$emit('rubricSubmitted', {
                                message: 'An error occurred.  Please try again later.'
                            });
                        }
                    );
                }
            }
        }
    });
})();
