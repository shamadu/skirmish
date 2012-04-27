/**
 * Author: Pavel Padinker
 * Date: 20.04.12
 * Time: 11:19
 */

var getCookie = function(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback_success, callback_error) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST"}).done(function(res) {
        callback_success(res)
    })
    .fail(function(res) {
        callback_error(res)
    });

};

jQuery.getJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "GET",
        success: function(response) {
            callback(response);
        }});
};

var logoutFunc = function () {
    $.getJSON('/logout', {}, function() {
        window.location.href='/login';
    });
};