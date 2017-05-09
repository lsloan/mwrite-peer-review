(function() {
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
