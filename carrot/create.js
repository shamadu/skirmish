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

    // ask server for class names
    $.postJSON('/info', {'action' : 'classes_list'}, function(res) {
        var myOptions = $.parseJSON(res);
        var mySelect = $("#classMenu");
        $.each(myOptions, function(val, text) {
            mySelect.append(
                $('<option></option>').val(val).html(text)
            );
        });
    });
};

var createFunc = function () {
    $.postJSON('/create', {"classID":document.getElementById("classMenu").selectedIndex}, function() {
        window.location.href='/';
    })
};
