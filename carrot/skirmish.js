/**
 * Created with PyCharm.
 * User: PavelP
 * Date: 17.04.12
 * Time: 11:00
 * To change this template use File | Settings | File Templates.
 */

var initialize = function () {
    $("#logoutButton").click(logoutFunc);
    $("#dropButton").click(dropFunc);
    $('a[data-toggle="tab"]').on('shown', function (e) {
        e.target // activated tab
        e.relatedTarget // previous tab
        window.alert("tab!");
    })
};

var logoutFunc = function () {
    $.getJSON('/logout', {}, function(res) {
        window.location.href='/login';
    });
};

var dropFunc = function () {
    $.getJSON('/drop', {}, function(res) {
        window.location.href='/create';
    });
};
