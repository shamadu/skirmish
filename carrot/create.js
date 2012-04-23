/**
 * Created with PyCharm.
 * User: Pavel
 * Date: 23.04.12
 * Time: 15:33
 * To change this template use File | Settings | File Templates.
 */

var initialize = function () {
    $("#createButton").click(onSelectClass);
};

var onSelectClass = function () {
    var formData = {
        "classID":document.getElementById("classMenu").selectedIndex
    };
    $.postJSON('/create', formData, function(res) {
        window.location.href='/';
    })

}
