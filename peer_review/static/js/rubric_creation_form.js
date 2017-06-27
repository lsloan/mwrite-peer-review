(function() {
    function populateIssuesList($container, issues) {
        var $issuesList = $container.find('ul.mdl-list');
        $issuesList.empty();
        if (issues.length === 0) {
            $container.addClass('hidden');
            $container.attr('data-has-fatal-issues', false);
        }
        else {
            for (var i = 0; i < issues.length; ++i) {
                var issueIcon = issues[i].fatal ? 'warning' : 'error_outline';
                var $element = $(
                    '<li class="mdl-list__item">' +
                        '<span class="mdl-list__item-primary-content">' +
                            '<i class="material-icons mdl-list__item-icon">' + issueIcon + '</i>' +
                            issues[i].message +
                        '</span>' +
                    '</li>'
                );
                $issuesList.append($element);
            }
            $container.removeClass('hidden');
            $container.attr('data-has-fatal-issues', someIssuesAreFatal(issues));
        }
    }

    function populateInfoParagraph($infoParagraph, validationsAreForPrompt, validations) {
        if (typeof(validations) !== 'undefined') {
            var sectionName = validations.sectionName || 'all students'; // TODO is this ok?
            var localDueDate = validations.localDueDate;
            if (sectionName !== null && localDueDate !== null) {
                var assignmentType = validationsAreForPrompt ? 'prompt' : 'revision';
                $infoParagraph.text('This ' + assignmentType + ' is assigned to ' + sectionName + ' and is due ' + localDueDate + '.');
                $infoParagraph.removeClass('hidden');
            }
            else {
                $infoParagraph.addClass('hidden');
            }
        }
    }

    function updateButtonState() {
        var fatalIssuesExist = $.map($('.validations-container'), function (e) {
                return $(e).attr('data-has-fatal-issues') === 'true';
            })
            .some(function (b) {
                return b;
            });
        $('button[type="submit"]').prop('disabled', fatalIssuesExist);
    }

    function updateValidationStatus($selectedMenu, assignmentId) {
        var validations = $('form').data('validation-info')[assignmentId];
        var validationsAreForPrompt = $selectedMenu.attr('id') === 'prompt-menu';
        var issues = getValidationIssues(validationsAreForPrompt, validations);
        var $assignmentCard = $selectedMenu.parents('.mdl-card');
        var $issuesContainer = $assignmentCard.find('.validations-container');
        var $infoParagraph = $assignmentCard.find('.assignment-info');
        populateIssuesList($issuesContainer, issues);
        populateInfoParagraph($infoParagraph, validationsAreForPrompt, validations);
        updateButtonState();
    }

    // TODO refactor for style / brevity
    function refreshMenuItems(items, menuID, withoutItems) {
        var $menu = $('#' + menuID);
        var $itemContainer = $('ul[for="' + menuID + '"]');
        $itemContainer.empty();
        if(menuID === 'revision-menu' && $menu.attr('data-selected-assignment-id') !== '') {
            var $noRevisionItem = $('<li></li>');
            $noRevisionItem.addClass('mdl-menu__item');
            $noRevisionItem.attr('data-assignment-id', '');
            $noRevisionItem.text('No revision');
            $noRevisionItem.click(selectAssignment);
            $itemContainer.append($noRevisionItem);
        }
        for(var id in items) {
            if(items.hasOwnProperty(id) && $.inArray(id, withoutItems) === -1) {
                var $item = $('<li></li>');
                $item.addClass('mdl-menu__item');
                $item.attr('data-assignment-id', id);
                $item.text(items[id]);
                $item.click(selectAssignment);
                $itemContainer.append($item);
            }
        }
        componentHandler.upgradeElement($menu.get(0));
    }

    function selectMenu($selectedMenu, caption, assignmentId) {
        $selectedMenu.find('span').text(caption);
        $selectedMenu.attr('data-selected-assignment-id', assignmentId);
        updateValidationStatus($selectedMenu, assignmentId);
    }

    // TODO compare with initializeMenus() and refactor
    function selectAssignment(event) {
        var $item = $(event.target);
        var $itemContainer = $item.closest('ul');
        var selectedMenuID = $itemContainer.attr('for');
        var $selectedMenu = $('#' + selectedMenuID);
        var otherMenuID = selectedMenuID === 'prompt-menu' ? 'revision-menu' : 'prompt-menu';

        selectMenu($selectedMenu, $item.text(), $item.attr('data-assignment-id'));

        var selectedAssignmentID = $item.attr('data-assignment-id');
        var otherSelectedAssignmentID = $('#' + otherMenuID).attr('data-selected-assignment-id');
        var withoutItems = [selectedAssignmentID, otherSelectedAssignmentID];

        var assignmentNamesByID = $('form').data('assignments');
        refreshMenuItems(assignmentNamesByID, selectedMenuID, withoutItems);
        refreshMenuItems(assignmentNamesByID, otherMenuID, withoutItems);
    }

    // TODO compare with selectAssignment() and refactor
    function initializeMenus() {
        var menusSelector = '#prompt-menu, #revision-menu';
        var withoutItems = [];
        var assignmentNamesByID = $('form').data('assignments');
        $(menusSelector).each(function(i, menu) {
            var $menu = $(menu);
            var existingSelectionID = $menu.attr('data-selected-assignment-id');
            if(existingSelectionID) {
                withoutItems.push(existingSelectionID);
                selectMenu($menu, assignmentNamesByID[existingSelectionID], existingSelectionID);
            }
        });
        $(menusSelector).each(function(i, menu) {
            refreshMenuItems(assignmentNamesByID, $(menu).attr('id'), withoutItems);
        });
    }

    function removeCriterionCard(event) {
        $(event.currentTarget).closest('.criterion-card').remove();
    }

    function addCriterionCard(event) {
        var template = $(event.currentTarget).attr('data-criterion-card-template');
        var $criteriaContainer = $('.criteria-container');
        var newIdNumber = parseInt($criteriaContainer.find('.criterion-card textarea').last().attr('id').split('-')[1]) + 1;
        var newId = 'criterion-' + newIdNumber + '-textarea';
        var $newCard = $(template);
        $newCard.find('textarea').attr('id', newId);
        $newCard.find('label').attr('for', newId);
        $newCard.find('button.mdl-chip__action').click(removeCriterionCard);
        var textField = $newCard.find('.mdl-textfield').get(0);
        autosize($(textField).find('textarea').get(0));
        componentHandler.upgradeElement(textField);
        $criteriaContainer.append($newCard);
    }

    function validateData(data) {
        if(!data.promptId) {
            showToast('You must select a prompt assignment.');
            return false;
        }
        if(!data.description) {
            showToast('You must provide a rubric description.');
            return false;
        }
        if(!data.criteria || data.criteria.length === 0) {
            showToast('You must enter at least one criterion.');
            return false;
        }
        return true;
    }

    function submitRubricForm(event) {
        var data = {
            promptId: parseInt($('#prompt-menu').attr('data-selected-assignment-id')) || null,
            revisionId: parseInt($('#revision-menu').attr('data-selected-assignment-id')) || null,
            description: $.trim($('#rubric-description-textfield').val()) || null,
            criteria: $.map($('.criterion-card textarea'), function(c) { return $.trim($(c).val()) || null; })
        };
        if(validateData(data)) {
            postToEndpoint(
                $('form').attr('action'),
                data,
                function() {
                    showToast('The rubric was successfully created.  You will be returned to the dashboard.');
                    setTimeout(function() { window.location.href = '/'; }, 4000);
                },
                function() {
                    showToast('An error occurred.  Please try again later.');
                }
            );
        }
        event.preventDefault();
    }

    //$(document).ready(function () {
    //    autosize($('textarea'));
    //    initializeMenus();
    //    $('#criteria-card').find('div.mdl-card__actions button').click(addCriterionCard);
    //    $('form').submit(submitRubricForm);
    //});

    // TODO remove everything above

    // TODO should this just be changed in the Django view?
    function assignmentsToOptions(assignments) {
        return _.map(assignments, function(val, key) {
            return {value: parseInt(key), name: val};
        });
    }

    new Vue({
        el: '#vue-root',
        components: _.defaults(VueMdl.components,
                               {'autosize-textarea': AutosizeTextarea}),
        directives: VueMdl.directives,
        mounted: function() {
            var $form = $('#rubric-form');
            this.assignments = assignmentsToOptions($form.data('assignments'));
            this.validations = $form.data('validation-info');
            this.existingPromptId = $form.data('selected-assignment-id');
            this.existingRevisionId = $form.data('selected-assignment-id');
            this.reviewIsInProgress = $form.data('review-is-in-progress');
            this.rubricDescription = $form.data('existing-rubric-description');
            // TODO grab existing criteria
        },
        data: {
            assignments: null,
            validations: null,
            reviewIsInProgress: null,
            selectedPromptId: null,
            selectedRevisionId: null,
            rubricDescription: null,
            criteria: [{id: 0, description: ''}],
            nextCriterionId: 1,

            existingPromptId: null,
            existingRevisionId: null
        },
        computed: {
            promptChoices: function() {
                if(this.assignments === null) {
                    return null;
                }

                var self = this;
                return _.filter(this.assignments, function(option) {
                    return option.value !== self.selectedRevisionId && option.value !== self.selectedPromptId;
                });
            },
            revisionChoices: function() {
                if(this.assignments === null) {
                    return null;
                }

                var self = this;
                var noRevisionOption = {value: null, name: 'No revision'};
                var revisionOptions = [noRevisionOption].concat(this.assignments);
                return _.filter(revisionOptions, function(option) {
                    if(typeof(option) !== 'undefined') {
                        return option.value === null || (option.value !== self.selectedPromptId && option.value !== self.selectedRevisionId);
                    }
                });
            },
            promptIssues: function() {
                return this.selectedPromptId !== null ? getValidationIssues(true, this.validations[this.selectedPromptId]) : [];
            },
            revisionIssues: function() {
                return this.selectedRevisionId !== null ? getValidationIssues(false, this.validations[this.selectedRevisionId]) : [];
            }
        },
        methods: {
            addCriterion: function() {
                this.criteria.push({id: this.nextCriterionId, description: ''});
                this.nextCriterionId++;
            },
            removeCriterion: function(id) {
                this.criteria = this.criteria.filter(function(criterion) {
                    return criterion.id !== id;
                });
            }
        }
    });
})();
