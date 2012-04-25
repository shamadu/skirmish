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
    updateCharacterInfo();

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

var joinFunc = function () {
    $.postJSON('/bot/battle', {'action' : 'join'}, function() {
        $('#joinLeaveButton').unbind('click');
        $("#joinLeaveButton").click(leaveFunc);
        $("#joinLeaveButton").html("Leave");
    });
};

var leaveFunc = function () {
    $.postJSON('/bot/battle', {'action' : 'leave'}, function() {
        $('#joinLeaveButton').unbind('click');
        $("#joinLeaveButton").click(joinFunc);
        $("#joinLeaveButton").html("Join");
    });
};

var updateCharacterInfo = function() {
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

        if (characterInfo.status == 'battle') {
            $("#joinLeaveButton").click(leaveFunc);
            $("#joinLeaveButton").html("Leave");
        }
        else {
            $("#joinLeaveButton").click(joinFunc);
            $("#joinLeaveButton").html("Join");
        }

        resize();
    });
}

var resize = function() {
    width = $("#characterInfoTable").width();
    $("#divMain").width(width);
    $("#divChat").css('right', width + 10 + 'px');

    width = $("#divUsers").width();
    $("#tabChat").css('right', width + 25 + 'px');
}