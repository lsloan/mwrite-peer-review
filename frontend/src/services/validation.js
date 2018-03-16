export function validationInfoAsIssues(validationInfo, validationsAreForPrompt = true) {
  const assignmentType = validationsAreForPrompt ? 'prompt' : 'revision';
  const errors = [];
  const warnings = [];

  if(validationInfo) {
    const {
      submissionUploadType,
      allowedSubmissionFileExtensions,
      localDueDate,
      numberOfDueDates,
      numberOfSections
    } = validationInfo;

    if(submissionUploadType.includes('none')) {
      errors.push({
        message: 'This ' + assignmentType + ' does not allow submissions.',
        fatal: true
      });
    }
    else {
      if(!submissionUploadType.includes('online_upload')) {
        errors.push({
          message: 'This ' + assignmentType + ' does not allow file upload submissions. ' +
                   'MWrite Peer Review requires these to retrieve submissions.',
          fatal: true
        });
      }

      submissionUploadType.forEach(type => {
        if(type !== 'online_upload') {
          warnings.push({
            message: 'This ' + assignmentType + ' allows ' + type.replace(/_/g, ' ') +
                     ' submissions.  MWrite Peer Review is not currently able to retrieve these.',
            fatal: false
          });
        }
      });

      if(allowedSubmissionFileExtensions === null || allowedSubmissionFileExtensions.length === 0) {
        warnings.push({
          message: 'This ' + assignmentType + ' does not restrict submission file extensions. ' +
                   'Be aware that students can submit files that their reviewers may not be able to open, ' +
                   'such as an Apple Pages document on a Windows PC.',
          fatal: false
        });
      }
    }

    if(localDueDate === null) {
      if(numberOfDueDates === 0) {
        const message = validationsAreForPrompt
          ? 'This prompt has no due date. This will prevent MWrite Peer Review from distributing submissions for review.'
          : 'This revision has no due date. This will prevent MWrite Peer Review from retrieving submissions.';
        errors.push({
          message: message,
          fatal: true
        });
      }
      else {
        if(validationsAreForPrompt && numberOfDueDates > 1) {
          errors.push({
            message: 'This prompt has multiple due dates.  This is currently unsupported.',
            fatal: true
          });
        }
      }
      if(validationsAreForPrompt && numberOfSections > 1) {
        errors.push({
          message: 'This prompt is assigned to multiple sections.  This is currently unsupported.',
          fatal: true
        });
      }
    }
  }

  return errors.concat(warnings);
};
