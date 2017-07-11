$(function() {
	$('.sortable').tablesorter({
		sortList:[[0,0], [1,0], [2,0], [3,0]]
	});

	$("tbody>tr").each(function() {
		var completed = $(this).find("td:eq(2)").text().split(/ +/)[0];
		var received = $(this).find("td:eq(3)").text().split(/ +/)[0];

		if (completed == '0') {
			$(this).find("td:eq(2)").css('color', '#E16877');
			$(this).find("td:eq(2)").css('font-weight', 600);
			$(this).css('background-color', '#F9EAEC');
		}

		if (received == '0') {
			$(this).find("td:eq(3)").css('color', '#E16877');
			$(this).find("td:eq(3)").css('font-weight', 600);
			$(this).css('background-color', '#F9EAEC');
		}
	})

	$('.dropbtn').on('click', function() {
		if ($('.dropdown-content').is(':visible')) {
			$('.dropdown-content').hide();
		} else {
			$('.dropdown-content').show();
		}
	});

	$(document).on("click", function(e) {
  		if(e.target.className != 'dropbtn' && e.target.className != 'dropdown-link') {
    		$('.dropdown-content').hide();
  		}
	});

	$('.dropdown-link').on('click', function() {
		console.log($(this).text());
	})
});