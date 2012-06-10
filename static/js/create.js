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
    $.postJSON('/create', {"race_id" : $("#raceMenu option:selected").val(), "class_id" : $("#classMenu option:selected").val()}, function() {
        window.location.href='/';
    })
};
