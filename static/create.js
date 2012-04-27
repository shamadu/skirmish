/**
 * Created with PyCharm.
 * User: Pavel
 * Date: 23.04.12
 * Time: 15:33
 * To change this template use File | Settings | File Templates.
 */

var initialize = function () {
    $("#createButton").click(createFunc);
    $("#logoutButton").click(logoutFunc);
};

var createFunc = function () {
    $.postJSON('/create', {"classID":document.getElementById("classMenu").selectedIndex}, function() {
        window.location.href='/';
    })
};
