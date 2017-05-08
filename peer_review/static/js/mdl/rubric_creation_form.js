(function() {
    window.removeCriterionCard = function(button) {
        $(button).closest('.criterion-card').remove();
    };

    window.addCriterionCard = function(template) {
        var $newCard = $(template);
        var textField = $newCard.find('.mdl-textfield').get(0);
        componentHandler.upgradeElement(textField);
        $('.criteria-container').append($newCard);
    };

    $(document).ready(function () {
        autosize($('textarea'));
    });
})();
