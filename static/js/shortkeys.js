$(function() {
    $(window).keyup(function(ev) {
        var number = ev.which - 48;
        $('button#labels-'+number).click();
    });
});
