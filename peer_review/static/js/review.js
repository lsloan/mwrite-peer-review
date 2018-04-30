(function() {
    function getReviewComments() {
        return $('[data-criterion-id]').map(function(index, element) {
            return {
                criterionID: $(element).attr('data-criterion-id'),
                comment: $(element).val()
            };
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

    function submitReview(event) {
        var comments = getReviewComments();
        if(areCommentsValid(comments)) {
            var $form = $('form');
            var endpoint = $form.attr('action');
            postToEndpoint(
                endpoint,
                comments,
                function () {
                    var frontendBaseUrl = $('[data-frontend-landing-url]').data('frontend-landing-url') + '/#';
                    window.location.replace(frontendBaseUrl + '/student/dashboard');
                },
                function () {
                    showToast('An error occurred.  Please try again later.');
                }
            );
        }
        else {
            showToast('Please comment on each criterion.');
        }
        event.preventDefault();
    }

    $(document).ready(function () {
        autosize($('textarea'));
        $('form').submit(submitReview);
    });
})();
