(function() {
    function populateIssuesList($container, issues) {
        var $issuesList = $container.find('ul.mdl-list');
        $issuesList.empty();
        if (issues.length === 0) {
            $container.addClass('hidden');
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
        }
    }

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
            if(items.hasOwnProperty(id) && $.inArray(parseInt(id), withoutItems) === -1) {
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

        var validations = $('form').data('validation-info')[assignmentId];
        var validationsAreForPrompt = $selectedMenu.attr('id') === 'prompt-menu';
        var issues = getValidationIssues(validationsAreForPrompt, validations);
        var $container = $selectedMenu.parents('.mdl-card').find('.validations-container');
        populateIssuesList($container, issues);
    }

    // TODO compare with initializeMenus() and refactor
    function selectAssignment(event) {
        var $item = $(event.target);
        var $itemContainer = $item.closest('ul');
        var selectedMenuID = $itemContainer.attr('for');
        var $selectedMenu = $('#' + selectedMenuID);
        var otherMenuID = selectedMenuID === 'prompt-menu' ? 'revision-menu' : 'prompt-menu';

        selectMenu($selectedMenu, $item.text(), $item.data('assignment-id'));

        var selectedAssignmentID = $item.data('assignment-id');
        var otherSelectedAssignmentID = $('#' + otherMenuID).data('selected-assignment-id');
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
            var existingSelectionID = $menu.data('selected-assignment-id');
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
        var $newCard = $(template);
        $newCard.find('button.mdl-chip__action').click(removeCriterionCard);
        var textField = $newCard.find('.mdl-textfield').get(0);
        componentHandler.upgradeElement(textField);
        $('.criteria-container').append($newCard);
    }

    $(document).ready(function () {
        autosize($('textarea'));
        initializeMenus();
        $('#criteria-card').find('div.mdl-card__actions button').click(addCriterionCard);
    });
})();
