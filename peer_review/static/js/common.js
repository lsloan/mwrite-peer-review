$(function() {
    $('.mdl-layout__header-row .mdl-navigation__link').on('click', function() {
        $('.mdl-layout__header-row').find('.mdl-navigation__link').removeClass("nav_link_click");
        $(this).addClass("nav_link_click");
    });

    if ($('.link_for_nav').hasClass('is_students')) {
    	$('.students').addClass('nav_link_click');
    } else if ($('.link_for_nav').hasClass('is_peer_review')) {
    	$('.peer_review').addClass('nav_link_click');
    }
});