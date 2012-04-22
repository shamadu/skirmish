/**
 * Created with PyCharm.
 * User: PavelP
 * Date: 17.04.12
 * Time: 11:00
 * To change this template use File | Settings | File Templates.
 */

function addEvent(obj, type, fn)
{
    if (obj.addEventListener)
        obj.addEventListener(type, fn, false);
    else if (obj.attachEvent)
        obj.attachEvent("on"+type, fn);
}

var initialize = function () {
    addEvent(document.getElementById("logoutButton"), "click", logoutFunc);

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
