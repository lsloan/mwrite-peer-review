$(function() {
    $('.sortable').tablesorter({
        sortList:[[0,0], [1,0], [2,0], [3,0]]
    });

    $(".student_entry").each(function() {
        var student_completed = ".student_completed";
        var student_received = ".student_received";
        var completed = $(this).find(student_completed).text().split(/ +/)[0];
        var received = $(this).find(student_received).text().split(/ +/)[0];
        var entry_with_zero = "entry_with_zero";
        var zero_completed_or_received = "zero_completed_or_received";

        if (completed == '0') {
            $(this).addClass(entry_with_zero);
            $(this).find(student_completed).addClass(zero_completed_or_received);
        }

        if (received == '0') {
            $(this).addClass(entry_with_zero);
            $(this).find(student_received).addClass(zero_completed_or_received);
        }
    })

    $(".dropbtn").on("click",function(){
        var dropdown_content = ".dropdown-content";

        if ($(dropdown_content).is(':visible')) {
            $(dropdown_content).hide();
        } else {
            $(dropdown_content).show();
        }
    });

    $(document).on("click", function(e) {
        if(e.target.className != 'dropbtn' && e.target.className !='dropdown-title' && e.target.className != 'material-icons dropdown-icon' && e.target.className != 'dropdown-link') {
            $('.dropdown-content').hide();
        }
    });

    $('.dropdown-link').on('click', function() {
        var section = $(this).text();
        var student_entry = ".student_entry";
        var student_section = ".student_section";

        if (section != "All Sections") {
            $(student_entry).each(function() {
                if($(this).find(student_section).text() == section) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        } else {
            $(student_entry).each(function() {
                $(this).show();
            });
        }
    });

    $(".table_header").on("click", function() {
        $(".header_icons").remove();

        if ($(this).hasClass("headerSortDown")) {
            $(this).append('<i class="material-icons header_icons">arrow_drop_down</i>');
        } else {
            $(this).append('<i class="material-icons header_icons">arrow_drop_up</i>');
        } 
    });
});