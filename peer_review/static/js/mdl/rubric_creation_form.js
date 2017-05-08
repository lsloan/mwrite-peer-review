(function() {
    function refreshMenuItems(items, menuID, withoutItems) {
        var $itemContainer = $('ul[for="' + menuID + '"]');
        $itemContainer.empty();
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
        componentHandler.upgradeElement($('#'+menuID).get(0));
    }

    function selectMenu(selectedAssignmentID, $selectedMenu, assignmentNamesByID) {
        $selectedMenu.find('span').text(assignmentNamesByID[selectedAssignmentID]);
        $selectedMenu.attr('selected-assignment-id', selectedAssignmentID);
    }

    // TODO compare with initializeMenus() and refactor
    function selectAssignment(event) {
        var $item = $(event.target);
        var $itemContainer = $item.closest('ul');
        var selectedMenuID = $itemContainer.attr('for');
        var $selectedMenu = $('#'+selectedMenuID);
        var otherMenuID = selectedMenuID === 'prompt-menu' ? 'revision-menu' : 'prompt-menu';

        var assignmentNamesByID = $('form').data('assignments');
        var selectedAssignmentID = $item.data('assignment-id');
        selectMenu(selectedAssignmentID, $selectedMenu, assignmentNamesByID);

        var otherSelectedAssignmentID = $('#' + otherMenuID).data('selected-assignment-id');
        var withoutItems = [selectedAssignmentID, otherSelectedAssignmentID];
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
                selectMenu(existingSelectionID, $menu, assignmentNamesByID);
            }
        });
        $(menusSelector).each(function(i, menu) {
            refreshMenuItems(assignmentNamesByID, $(menu).attr('id'), withoutItems);
        });
    }

    // TODO set this in $(document).ready(...) rather than as onclick attrs
    window.removeCriterionCard = function(button) {
        $(button).closest('.criterion-card').remove();
    };

    // TODO set this in $(document).ready(...) rather than as onclick attrs
    window.addCriterionCard = function(template) {
        var $newCard = $(template);
        var textField = $newCard.find('.mdl-textfield').get(0);
        componentHandler.upgradeElement(textField);
        $('.criteria-container').append($newCard);
    };

    $(document).ready(function () {
        autosize($('textarea'));
        initializeMenus();
    });
})();
