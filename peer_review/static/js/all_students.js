$(function() {

    $('.sortable').tablesorter({
        sortList: [[0,0], [1,0]]
    });

    var courseId = $('#main-container').data('course-id');
    var studentEntrySelector = ".student_entry";

    $('.dropbtn').click(function() {
        var dropdown_content = ".dropdown-content";

        if ($(dropdown_content).is(':visible')) {
            $(dropdown_content).hide();
        } else {
            $(dropdown_content).show();
        }
    });

    $(document).click(function(e) {
        if(e.target.className !== 'dropbtn' && e.target.className !== 'dropdown-title' && e.target.className !== 'material-icons dropdown-icon' && e.target.className !== 'dropdown-link') {
            $('.dropdown-content').hide();
        }
    });

    $('.dropdown-link').click(function() {

        var selectedSectionId = $(this).data('section-id');

        if(selectedSectionId !== 'all') {
            $(studentEntrySelector).each(function() {
                var studentEntrySections = $(this).data('sections');
                if($.inArray(selectedSectionId, studentEntrySections) !== -1) {
                    $(this).show();
                }
                else {
                    $(this).hide();
                }
            });
        }
        else {
            $(studentEntrySelector).each(function() {
                $(this).show();
            });
        }

        $('.dropdown-content').hide();
    });

    $(".table_header").on("click", function() {
        $(".header_icons").remove();

        if ($(this).hasClass("headerSortDown")) {
            $(this).append('<i class="material-icons header_icons">arrow_drop_down</i>');
        } else {
            $(this).append('<i class="material-icons header_icons">arrow_drop_up</i>');
        }
    });

    $(studentEntrySelector).click(function() {
        var studentId = $(this).attr('data-student-id');
        window.location = '/course/' + courseId + '/review/student/' + studentId;
    });
});