/* e
xported getValidationIssues */
function getValidationIssues(validationsAreForPrompt, validations) {

    var assignmentType = validationsAreForPrompt ? 'prompt' : 'revision';
    var errors = [];
    var warnings = [];

    if(typeof(validations) !== 'undefined') {
        if(validations.submissionUploadType.includes('none')) {
            errors.push({
                message: 'This ' + assignmentType + ' does not allow submissions.',
                fatal: true,
            });
        }
        else {
            if(!validations.submissionUploadType.includes('online_upload')) {
                errors.push({
                    message: 'This ' + assignmentType + ' does not allow file upload submissions. ' +
                            'MWrite Peer Review requires these to retrieve submissions.',
                    fatal: true
                });
            }

            for(var i = 0; i < validations.submissionUploadType.length; ++i) {
                var submissionUploadType = validations.submissionUploadType[i];
                if(submissionUploadType !== 'online_upload') {
                    warnings.push({
                        message: 'This ' + assignmentType + ' allows ' + submissionUploadType.replace(/_/g, ' ') +
                                 ' submissions.  MWrite Peer Review is not currently able to retrieve these.',
                        fatal: false
                    });
                }
            }

            if(validations.allowedSubmissionFileExtensions === null || validations.allowedSubmissionFileExtensions.length == 0) {
                warnings.push({
                    message: 'This ' + assignmentType + ' does not restrict submission file extensions. ' +
                             'Be aware that students can submit files that their reviewers may not be able to open, such as ' +
                             'an Apple Pages document on a Windows PC.',
                    fatal: false
                });
            }
        }

        if(validations.localDueDate === null) {
            if(validations.numberOfDueDates === 0) {
                var message = validationsAreForPrompt ?
                    'This prompt has no due date. This will prevent MWrite Peer Review from distributing submissions for review.' :
                    'This revision has no due date. This will prevent MWrite Peer Review from retrieving submissions.';
                errors.push({
                    message: message,
                    fatal: true
                });
            }
            else {
                if(validationsAreForPrompt && validations.numberOfDueDates > 1) {
                    errors.push({
                        message: 'This prompt has multiple due dates.  This is currently unsupported.',
                        fatal: true
                    });
                }
            }
            if(validationsAreForPrompt && validations.numberOfSections > 1) {
                errors.push({
                    message: 'This prompt is assigned to multiple sections.  This is currently unsupported.',
                    fatal: true
                });
            }
        }
    }

    return errors.concat(warnings);
}

/* exported populateIssuesList */
function populateIssuesList(validationsAreForPrompt, issues) {
    var issuesContainer = validationsAreForPrompt ? $('#prompt-issues-container') : $('#revision-issues-container');
    var issuesList = issuesContainer.find('ul.collection');
    issuesList.empty();
    
    if(issues.length === 0) {
        issuesContainer.addClass('hide');
    }
    else {
        for(var i = 0; i < issues.length; ++i) {
            var issueClass = issues[i].fatal ? 'red lighten-1' : 'yellow lighten-1';
            var issueIcon = issues[i].fatal ? 'warning' : 'error_outline';
            var element =
                '<li class="collection-item ' + issueClass + '">' +
                '<div class="flex-container">' +
                '<div><i class="material-icons left">' + issueIcon + '</i></div>' +
                '<div>' + issues[i].message + '</div>' +
                '</div>' +
                '</li>';
            issuesList.append(element);
        }
        issuesContainer.removeClass('hide');
    }
}

/* exported populateInfoParagraph */
function populateInfoParagraph(validationsAreForPrompt, validations) {
    if(typeof(validations) !== 'undefined') {
        var sectionName = validations.sectionName || 'all students'; // TODO is this ok?
        var localDueDate = validations.localDueDate
        var infoParagraph = validationsAreForPrompt ? $('#prompt-info') : $('#revision-info');
        if(sectionName !== null && localDueDate !== null) {
            var assignmentType = validationsAreForPrompt ? 'prompt' : 'revision';
            infoParagraph.text('This ' + assignmentType + ' is assigned to ' + sectionName + ' and is due ' + localDueDate + '.');
            infoParagraph.removeClass('hide');
        }
        else {
            infoParagraph.addClass('hide');
        }
    }
}

/* exported someIssuesAreFatal */
function someIssuesAreFatal(issues) {
    return $.grep(issues, function(i) { return i.fatal }).length > 0;
}

/* exported updatePromptValidationStatus */
function updateValidationStatus(select) {
    var validationsInfo = $('#rubric-data').data('validations');
    var assignmentId = select.val();
    var validations = validationsInfo[assignmentId];
    var validationsAreForPrompt = select.parents('[data-selector-parent]').attr('id') == 'prompt-selector-parent';
    populateInfoParagraph(validationsAreForPrompt, validations);
    var issues = getValidationIssues(validationsAreForPrompt, validations);
    populateIssuesList(validationsAreForPrompt, issues);

    var otherSelect = validationsAreForPrompt ? $('#revision-selector-parent').find('select') : $('#prompt-selector-parent').find('select');
    var otherAssignmentId = otherSelect.val();
    var otherValidations = validationsInfo[otherAssignmentId];
    var allIssues = issues.concat(getValidationIssues(!validationsAreForPrompt, otherValidations));
    $('[data-submit-button]').prop('disabled', someIssuesAreFatal(allIssues));
}
