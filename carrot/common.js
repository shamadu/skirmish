/**
 * Created with PyCharm.
 * User: PavelP
 * Date: 20.04.12
 * Time: 11:19
 * To change this template use File | Settings | File Templates.
 */

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST"}).done(function(res) {
        callback(res)
    });
};

jQuery.getJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "GET",
        success: function(response) {
            callback(response);
        }});
};