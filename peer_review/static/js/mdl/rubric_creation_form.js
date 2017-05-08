(function() {
    window.removeCriterionCard = function(button) {
        $(button).closest('.criterion-card').remove()
    };

    $(document).ready(function () {
        autosize($('textarea'));
    });
})();
