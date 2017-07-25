$(function() {
    $('.each_review').each(function() {
        if ($(this).find(".each_review_link").attr('href') == window.location.href.replace(window.location.origin, '')) {
            $(this).addClass("show_border");
            $(this).find(".each_review_link").addClass("change_link_style");
        }
    });

    $('.download_title').on('click', function() {
        var csrf = $('meta[name="csrf"]').attr('content')

        $.ajax ({
            type: 'get',
            url: '',
            dataType: 'json',
            data: {csrfmiddlewaretoken: csrf},
        });
    });
});
