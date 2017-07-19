$(function() {
	$('.each_review').each(function() {
		console.log($(this).find(".each_review_link").attr('href'));
		console.log(window.location.href.replace(window.location.origin, ''));
		if ($(this).find(".each_review_link").attr('href') == window.location.href.replace(window.location.origin, '')) {
			$(this).addClass("show_border");
			$(this).find(".each_review_link").addClass("change_link_style");
		}
	});
});
