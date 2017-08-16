$(function() {
    $('.each_review').each(function() {
        if($(this).find(".each_review_link").attr('href') === window.location.href.replace(window.location.origin, '')) {
            $(this).addClass("show_border");
            $(this).find(".each_review_link").addClass("change_link_style");
        }
    });

    $('.download_title').on('click', function() {
        var courseId = $('#main-container').data('course-id');
        var student_id = $('.student_link').attr('data-student-id');

        var hrefPrefix = '/course/' + courseId + '/review/student/' + student_id;
        var $textOnNav = $('.text_on_nav');
        if($textOnNav.text() === 'Overview') {
            window.location.href = hrefPrefix + '/download';
        }
        else {
            var rubric_id = $textOnNav.attr('data-rubric-id');
            window.location.href = hrefPrefix + '/rubric/' + rubric_id + '/download';
        }
    });
});
