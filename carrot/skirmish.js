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
    $.postJSON('/info', {'action' : 'character_info'}, function(res) {
        var characterInfo = $.parseJSON(res);
        $("#nameLabel").text(characterInfo.name);
        $("#classLabel").text(characterInfo.char_class);
        $("#levelLabel").text(characterInfo.level);
        $("#HPLabel").text(characterInfo.hp);
        $("#MPLabel").text(characterInfo.mp);
        $("#strengthLabel").text(characterInfo.strength);
        $("#dexterityLabel").text(characterInfo.dexterity);
        $("#intellectLabel").text(characterInfo.intellect);
        $("#wisdomLabel").text(characterInfo.wisdom);

        width = $("#characterInfoTable").width();
        $("#divMain").width(width);
        $("#divChat").css('right', width + 25 + 'px');
    });

    $('a[data-toggle="tab"]').on('shown', function (e) {
        e.target // activated tab
        e.relatedTarget // previous tab
        window.alert("tab!");
    })
};

var dropFunc = function () {
    $.getJSON('/drop', {}, function() {
        window.location.href='/create';
    });
};
