/**
 * Author: Pavel Padinker
 * Date: 19.04.12
 * Time: 12:38
 */

var initialize = function () {
    $("#loginButton").click(loginFunc);
    $("#passwordText").keypress(keyPress);
    $("#locales").change(selectLocale);
};

var loginFunc = function () {
    setCookie("locale", $("#locales option:selected").val());
    var formData = {
        "login":$("#loginText").val()
        , "password":$("#passwordText").val()
    };
    $.postJSON('/login', formData, function(res) {
        var login_response = $.parseJSON(res)
        if (login_response.error) {
            $("#errorLabel").html(login_response.msg);
        }
        else {
            window.location.href='/';
        }
    })
};

var keyPress = function(event) {
    if ( event.which == 13 ) {
        loginFunc();
    }
}
