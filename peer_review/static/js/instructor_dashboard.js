function updateValidationIcon(validationsInfo, container) {
    var promptId = container.data('prompt-id');
    var revisionId = container.data('revision-id');
    var promptValidations = validationsInfo[promptId];
    var revisionValidations = validationsInfo[revisionId];
    var promptIssues = promptId ? getValidationIssues(true, promptValidations) : [];
    var revisionIssues = revisionId ? getValidationIssues(false, revisionValidations) : [];
    var validationIcon = container.find('i.material-icons');
    var validationCaption = container.find('p');
    var allIssues = promptIssues.concat(revisionIssues);
    if(allIssues.length > 0) {
        var rubricHasFatalIssues = someIssuesAreFatal(allIssues);
        var icon = rubricHasFatalIssues ? 'warning' : 'error_outline';
        var action = container.data('reviews-in-progress') ? 'view' : 'edit';
        var caption = rubricHasFatalIssues ?
            'Error: ' + action + ' the rubric to see problems' :
            'Warning: ' + action + ' the rubric to view our suggested changes';
        validationIcon.text(icon);
        validationIcon.removeClass('ok-icon');
        validationIcon.addClass(rubricHasFatalIssues ? 'error-icon' : 'warning-icon');
        validationCaption.removeClass('ok-caption');
        validationCaption.text(caption);
    }
    container.find('.hide-but-keep-space').removeClass('hide-but-keep-space');
}

$('document').ready(function () {
    var validationsInfo = $('[data-peer-review-assignments-parent]').data('peer-review-assignments-parent');
    $('[data-rubric-card]').each(function(i, element) {
        updateValidationIcon(validationsInfo, $(element));
    });
});

