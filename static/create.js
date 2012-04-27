/**
 * Author: Pavel Padinker
 * Date: 23.04.12
 * Time: 15:33
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
