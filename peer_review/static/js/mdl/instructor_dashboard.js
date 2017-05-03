(function () {
    function someIssuesAreFatal(issues) {
        return $.grep(issues, function (i) {
                return i.fatal
            }).length > 0;
    }

    function getValidationIssues(validationsAreForPrompt, validations) {

        var assignmentType = validationsAreForPrompt ? 'prompt' : 'revision';
        var errors = [];
        var warnings = [];

        if (typeof(validations) !== 'undefined') {
            if (validations.submissionUploadType.includes('none')) {
                errors.push({
                    message: 'This ' + assignmentType + ' does not allow submissions.',
                    fatal: true,
                });
            }
            else {
                if (!validations.submissionUploadType.includes('online_upload')) {
                    errors.push({
                        message: 'This ' + assignmentType + ' does not allow file upload submissions. ' +
                        'MWrite Peer Review requires these to retrieve submissions.',
                        fatal: true
                    });
                }

                for (var i = 0; i < validations.submissionUploadType.length; ++i) {
                    var submissionUploadType = validations.submissionUploadType[i];
                    if (submissionUploadType !== 'online_upload') {
                        warnings.push({
                            message: 'This ' + assignmentType + ' allows ' + submissionUploadType.replace(/_/g, ' ') +
                            ' submissions.  MWrite Peer Review is not currently able to retrieve these.',
                            fatal: false
                        });
                    }
                }

                if (validations.allowedSubmissionFileExtensions === null || validations.allowedSubmissionFileExtensions.length == 0) {
                    warnings.push({
                        message: 'This ' + assignmentType + ' does not restrict submission file extensions. ' +
                        'Be aware that students can submit files that their reviewers may not be able to open, such as ' +
                        'an Apple Pages document on a Windows PC.',
                        fatal: false
                    });
                }
            }

            if (validations.localDueDate === null) {
                if (validations.numberOfDueDates === 0) {
                    var message = validationsAreForPrompt ?
                        'This prompt has no due date. This will prevent MWrite Peer Review from distributing submissions for review.' :
                        'This revision has no due date. This will prevent MWrite Peer Review from retrieving submissions.';
                    errors.push({
                        message: message,
                        fatal: true
                    });
                }
                else {
                    if (validationsAreForPrompt && validations.numberOfDueDates > 1) {
                        errors.push({
                            message: 'This prompt has multiple due dates.  This is currently unsupported.',
                            fatal: true
                        });
                    }
                }
                if (validationsAreForPrompt && validations.numberOfSections > 1) {
                    errors.push({
                        message: 'This prompt is assigned to multiple sections.  This is currently unsupported.',
                        fatal: true
                    });
                }
            }
        }

        return errors.concat(warnings);
    }

    function updateValidationText(validationsInfo, $peerReviewCard) {
        var promptId = $peerReviewCard.data('prompt-id');
        var revisionId = $peerReviewCard.data('revision-id');
        var promptValidations = validationsInfo[promptId];
        var revisionValidations = validationsInfo[revisionId];
        var promptIssues = promptId ? getValidationIssues(true, promptValidations) : [];
        var revisionIssues = revisionId ? getValidationIssues(false, revisionValidations) : [];
        var allIssues = promptIssues.concat(revisionIssues);

        var $validationIcon = $peerReviewCard.find('.material-icons');
        var $validationCaption = $peerReviewCard.find('.validation-caption');

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
