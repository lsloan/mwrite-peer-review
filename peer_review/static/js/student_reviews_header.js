$(function() {
    $('.each_review').each(function() {
        if ($(this).find(".each_review_link").attr('href') == window.location.href.replace(window.location.origin, '')) {
            $(this).addClass("show_border");
            $(this).find(".each_review_link").addClass("change_link_style");
        }
    });

    $('.download_title').on('click', function() {
        student_id = $('.student_link').attr('data-student-id');

        if ($('.text_on_nav').text() == 'Overview') {
            window.location.href = '/review/student/'+ student_id +'/download';
        } else {
            rubric_id = $('.text_on_nav').attr('data-rubric-id');
            window.location.href = '/review/student/'+ student_id +'/rubric/'+ rubric_id +'/download';
        }
    });
});
