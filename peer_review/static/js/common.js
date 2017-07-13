$(function() {
	$('.mdl-layout__header-row .mdl-navigation__link').on('click', function() {
        $('.mdl-layout__header-row').find('.mdl-navigation__link').removeClass("nav_link_click");
        $(this).addClass("nav_link_click");
    });
});