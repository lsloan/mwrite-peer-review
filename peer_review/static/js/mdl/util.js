(function () {
    function makePostParams(endpoint, data, csrfTokenSelector) {
        var _csrfTokenSelector = csrfTokenSelector || 'input[name="csrfmiddlewaretoken"]';
        return {
            type: 'POST',
            url: endpoint,
            data: JSON.stringify(data),
            contentType: 'application/json',
            headers: {
                'X-CSRF-Token': $(_csrfTokenSelector).val()
            }
        };
    }

    window.postToEndpoint = function(endpoint, data, successAction, failureAction) {
        var _successAction = successAction || function() {};
        var _failureAction = failureAction || function() {};
        $.ajax(makePostParams(endpoint, data)).done(_successAction).fail(_failureAction);
    };

    window.showToast = function(message) {
        $('#snackbar').get(0).MaterialSnackbar.showSnackbar({message: message});
    };
})();
