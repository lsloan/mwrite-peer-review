/* eslint-env jquery */
/* global Materialize */
/* global postToEndpoint */
/* global showGenericErrorMessage */

function getReviewComments() {
    return $('[data-criterion-id]').map(function(index, element) {
        return {criterionID: $(element).attr('data-criterion-id'),
                comment: $(element).val()};
    }).get();
}

function areCommentsValid(comments) {
    for(var i = 0; i < comments.length; ++i) {
        if(!comments[i].comment.trim()) {
            return false;
        }
    }
    return true;
}

/* exported submitReview */
function submitReview(promptId) {
    var comments = getReviewComments();
    if(!areCommentsValid(comments)) {
        Materialize.toast('Please comment on each criterion.', 5000);
        return;
    }
    var endpoint = $('[data-comment-form]').attr('action');
    var submitButton = $('[data-submit-button]');
    postToEndpoint(endpoint,
                   submitButton,
                   function() {
                       window.location.replace('/dashboard/student?finished=' + promptId);
                   },
                   showGenericErrorMessage,
                   comments);
}

