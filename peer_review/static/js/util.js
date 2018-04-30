(function () {
    function makePostParams(endpoint, data, csrfTokenSelector) {
        var _csrfTokenSelector = csrfTokenSelector || 'input[name="csrfmiddlewaretoken"]';
        return {
            type: 'POST',
            url: endpoint,
            data: JSON.stringify(data),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': $(_csrfTokenSelector).val()
            }
        };
    }

    window.postToEndpoint = function(endpoint, data, successAction, failureAction, finallyAction) {
        var doNothing = function() {};
        var _successAction = successAction || doNothing;
        var _failureAction = failureAction || doNothing;
        var _finallyAction = finallyAction || doNothing;
        $.ajax(makePostParams(endpoint, data)).done(_successAction).fail(_failureAction).always(_finallyAction);
    };

    window.showToast = function(message) {
        $('#snackbar').get(0).MaterialSnackbar.showSnackbar({message: message});
    };
})();
