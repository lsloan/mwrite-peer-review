(function() {
    window.someIssuesAreFatal = function(issues) {
        return $.grep(issues, function (i) {
                return i.fatal
            }).length > 0;
    };

    window.getValidationIssues = function(validationsAreForPrompt, validations) {
        var assignmentType = validationsAreForPrompt ? 'prompt' : 'revision';
        var errors = [];
        var warnings = [];

        if (typeof(validations) !== 'undefined') {
            if (validations.submissionUploadType.includes('none')) {
                errors.push({
                    message: 'This ' + assignmentType + ' does not allow submissions.',
                    fatal: true
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
    };
})();
