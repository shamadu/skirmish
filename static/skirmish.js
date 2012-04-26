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
    $("#sendButton").click(sendFunc);
    $("#sendTextArea").keypress(keyPress);
    updateCharacterInfo();
    $.postJSON('/bot/users/onstart', {}, function(res) {
        var users = $.parseJSON(res);
        updateUsers(users)
    });

    $('a[data-toggle="tab"]').on('shown', function (e) {
        e.target // activated tab
        e.relatedTarget // previous tab
        window.alert("tab!");
    });
    messager.poll();
    users_updater.poll();
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
};

var updateUsers = function(users) {
    // clear div and add labels to divUsers
};

var resize = function() {
    width = $("#characterInfoTable").width();
    $("#divMain").width(width);
    $("#divChat").css('right', width + 25 + 'px');

    width = $("#divUsers").width();
    $("#tabChat").css('right', width + 25 + 'px');
};

var sendFunc = function() {
    data = {
        'to' : 'all',
        'body' : $("#sendTextArea").val()
    };
    $("#sendTextArea").val("");
    $("#sendTextArea").focus();
    $.postJSON('/bot/message/new', data, function() {
    });
};

var keyPress = function(event) {
    // mozilla has 13 key for enter with/without ctrl, chrome and IE
    // have 10 key if enter is pressed with ctrl
    if ((event.which == 10 || event.which == 13 )&& event.ctrlKey) {
        sendFunc();
    }
};

var messager = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/bot/message/poll', {}, messager.onSuccess, messager.onError);
    },

    onSuccess: function(response) {
        var message = $.parseJSON(response);
        if(message.to == "all") {
            today = new Date();
            message_formatted = "[" + today.getHours() + ":" + today.getMinutes() + ":" +
            + today.getSeconds() + "]<" + message.from + ">: " + message.body + "\n";
            $("#enTextArea").val($("#enTextArea").val() + message_formatted);
        }

        messager.errorSleepTime = 500;
        window.setTimeout(messager.poll, 0);
    },

    onError: function(response) {
        messager.errorSleepTime *= 2;
        window.setTimeout(messager.poll, messager.errorSleepTime);
    }
};

var users_updater = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/bot/users/poll', {}, users_updater.onSuccess, users_updater.onError);
    },

    onSuccess: function(response) {
        var users = $.parseJSON(response);
        updateUsers(users)

        users_updater.errorSleepTime = 500;
        window.setTimeout(users_updater.poll, 0);
    },

    onError: function(response) {
        users_updater.errorSleepTime *= 2;
        window.setTimeout(users_updater.poll, users_updater.errorSleepTime);
    }
};