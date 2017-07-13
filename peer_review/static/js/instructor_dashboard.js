(function () {
    function updateValidationText(validationsInfo, $peerReviewCard) {
        var promptId = $peerReviewCard.data('prompt-id');
        var revisionId = $peerReviewCard.data('revision-id');
        var promptValidations = validationsInfo[promptId];
        var revisionValidations = validationsInfo[revisionId];
        var promptIssues = promptId ? getValidationIssues(true, promptValidations) : [];
        var revisionIssues = revisionId ? getValidationIssues(false, revisionValidations) : [];
        var allIssues = promptIssues.concat(revisionIssues);

        var $validationContainer = $peerReviewCard.find('.validation-container');
        var $validationIcon = $validationContainer.find('.material-icons');
        var $validationCaption = $validationContainer.find('.icon-caption');

        if (allIssues.length > 0) {
            var rubricHasFatalIssues = someIssuesAreFatal(allIssues);
            var action = $peerReviewCard.data('reviews-in-progress') ? 'view' : 'edit';
            $validationIcon.text(rubricHasFatalIssues ? 'warning' : 'error_outline');
            $validationIcon.removeClass('ok-icon-color');
            $validationIcon.addClass(rubricHasFatalIssues ? 'error-icon-color' : 'warning-icon-color');
            $validationCaption.text(
                rubricHasFatalIssues ?
                    'Error: ' + action + ' the rubric to see problems.' :
                    'Warning: ' + action + ' the rubric to view our suggested changes.'
            );
        }
    }

    $('document').ready(function () {
        var validationsInfo = $('[data-validations-info]').data('validations-info');
        $('.peer-review-assignment-card').each(function (i, element) {
            var $peerReviewCard = $(element);
            updateValidationText(validationsInfo, $peerReviewCard);
        });
    });
})();
