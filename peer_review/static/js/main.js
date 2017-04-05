/* eslint-env jquery */
/* global Materialize */

function setButtonState(button, shouldBeDisabled) {
    var _button = $(button);
    _button.prop('disable', shouldBeDisabled);
    _button.toggleClass('disabled', shouldBeDisabled);
}

/* exported postToEndpoint */
function postToEndpoint(endpoint, submitButton, successAction, failureAction, data) {
    var antiForgeryToken = $('#__anti-forgery-token').val();
    setButtonState(submitButton, true);
    $.ajax({
        type: 'POST',
        url: endpoint,
        data: JSON.stringify(data),
        contentType: 'application/json',
        headers: {
            'X-CSRF-Token': antiForgeryToken
        }
    })
    .done(successAction)
    .fail(failureAction)
    .always(function() {
        setButtonState(submitButton, false);
    });
}

/* exported showGenericErrorMessage */
var defaultToastDuration = 5000;
function showGenericErrorMessage() {
    Materialize.toast('An error occurred.  Please try again later.', defaultToastDuration);
}

