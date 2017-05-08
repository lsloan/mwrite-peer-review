(function() {
    function refreshMenuItems(items, menuID, withoutItems) {
        var $menu = $('#'+menuID);
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

    function selectMenu($selectedMenu, $item) {
        $selectedMenu.find('span').text($item.text());
        $selectedMenu.attr('data-selected-assignment-id', $item.data('assignment-id'));
    }

    // TODO compare with initializeMenus() and refactor
    function selectAssignment(event) {
        var $item = $(event.target);
        var $itemContainer = $item.closest('ul');
        var selectedMenuID = $itemContainer.attr('for');
        var $selectedMenu = $('#'+selectedMenuID);
        var otherMenuID = selectedMenuID === 'prompt-menu' ? 'revision-menu' : 'prompt-menu';

        selectMenu($selectedMenu, $item);

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
