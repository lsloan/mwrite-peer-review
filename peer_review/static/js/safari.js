function launchForSafari(canvasToolUrl) {
    var popup = window.open('/safari', 'toolbar=no,status=no,width=100,height=100');
    $(popup).on('load', function() {
        popup.close();
        window.parent.location.href = canvasToolUrl;
    });
}

