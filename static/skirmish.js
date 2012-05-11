/**
 * Author: Pavel Padinker
 * Date: 17.04.12
 * Time: 11:00
 */

var initialize = function () {
    $("#logoutButton").click(logoutFunc);
    $("#dropButton").click(dropButtonClick);
    $("#sendButton").click(sendFunc);
    $("#sendTextArea").keypress(keyPress);
    $("#joinButton").attr('disabled', true);
    $("#leaveButton").attr('disabled', true);
    $("#leaveButton").hide();
    $("#joinButton").click(joinButtonClick);
    $("#leaveButton").click(leaveButtonClick);
    updateCharacterInfo();

    $('a[data-toggle="tab"]').on('shown', function (e) {
        e.target // activated tab
        e.relatedTarget // previous tab
        window.alert("tab!");
    });
    messager.poll();
    onlineUsersUpdater.poll();
    battleBotUpdater.poll();
};

var dropButtonClick = function () {
    leaveButtonClick();
    $.getJSON('/drop', {}, function() {
        window.location.href='/create';
    });
};

var joinButtonClick = function () {
    $.postJSON('/bot/battle', {'action' : 'join'}, function() {
    });
};

var leaveButtonClick = function () {
    $.postJSON('/bot/battle', {'action' : 'leave'}, function() {
    });
};

var updateCharacterInfo = function() {
    $.postJSON('/info', {}, function(res) {
        var characterInfo = $.parseJSON(res);
        $("#nameLabel").text(characterInfo.name);
        $("#classLabel").text(characterInfo.className);
        $("#levelLabel").text(characterInfo.level);
        $("#HPLabel").text(characterInfo.hp);
        $("#MPLabel").text(characterInfo.mp);
        $("#strengthLabel").text(characterInfo.strength);
        $("#dexterityLabel").text(characterInfo.dexterity);
        $("#intellectLabel").text(characterInfo.intellect);
        $("#wisdomLabel").text(characterInfo.wisdom);
    });
};

var resize = function() {
    width = $("#characterInfoTable").width();
    $("#divChat").css('right', width + 15 + 'px');

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
    $.postJSON('message/new', data, function() {
    });
};

var keyPress = function(event) {
    // mozilla has 13 key for enter with/without ctrl, chrome and IE
    // have 10 key if enter is pressed with ctrl
    if ((event.which == 10 || event.which == 13 )) {
        if(event.ctrlKey) {
            $("#sendTextArea").val($("#sendTextArea").val() + "\n");
            $("#sendTextArea").focus();
        }
        else {
            sendFunc();
        }
    }
};

var format_message = function(message) {
    today = new Date();
    hours = today.getHours();
    if(hours < 10) {
        hours = "0" + hours;
    }
    minutes = today.getMinutes();
    if(minutes < 10) {
        minutes = "0" + minutes;
    }
    seconds = today.getSeconds();
    if(seconds < 10) {
        seconds = "0" + seconds;
    }

    body_lines = message.body.split("\n");
    message_formatted = "";
    for(line in body_lines){
        message_formatted += "[" + hours + ":" + minutes + ":" + seconds + "]<" + message.from + ">: " + body_lines[line] + "\n";
    }

    return message_formatted;
};

var addTextTo = function(element_id, message) {
    element = $(element_id)
    element.val(element.val() + message);
    element.scrollTop(element[0].scrollHeight - element.height());
}

var messager = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/message/poll', {}, messager.onSuccess, messager.onError);
    },

    onSuccess: function(response) {
        var message = $.parseJSON(response);
        if(message.to == "all") {
            addTextTo("#enTextArea", format_message(message))
        }

        messager.errorSleepTime = 500;
        window.setTimeout(messager.poll, 0);
    },

    onError: function() {
        messager.errorSleepTime *= 2;
        window.setTimeout(messager.poll, messager.errorSleepTime);
    }
};

var onlineUsersUpdater = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/users/poll', {}, onlineUsersUpdater.onSuccess, onlineUsersUpdater.onError);
    },

    onSuccess: function(response) {
        updateOnlineUsers(response);

        onlineUsersUpdater.errorSleepTime = 500;
        window.setTimeout(onlineUsersUpdater.poll, 0);
    },

    onError: function() {
        onlineUsersUpdater.errorSleepTime *= 2;
        window.setTimeout(onlineUsersUpdater.poll, onlineUsersUpdater.errorSleepTime);
    }
};

var updateOnlineUsers = function(users) {
    $("#divOnlineUsers").empty();
    var online_users = String(users).split(',');
    if (online_users.length != 0 && online_users[0].length != 0) {
        for (i = 0; i < online_users.length; ++i) {
            $("#divOnlineUsers").append("<label>" + online_users[i] + "</label>")
        }
    }

    resize()
};

var battleBotUpdater = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/bot/poll', {}, battleBotUpdater.onSuccess, battleBotUpdater.onError);
    },

    onSuccess: function(response) {
        var action = $.parseJSON(response);
        // update skirmish users
        if(action.type == 0) {
            updateSkirmishUsers(action.skirmish_users);
        }
        // can join
        else if(action.type == 1) {
            $("#joinButton").removeAttr('disabled');
            $("#joinButton").show();
            $("#leaveButton").hide();
        }
        // can leave
        else if(action.type == 2) {
            $("#leaveButton").show();
            $("#leaveButton").removeAttr('disabled');
            $("#joinButton").hide();
        }
        // can do turn
        else if(action.type == 3) {
            removeDivAction();
            showDivAction(action.div_action);
        }
        // can cancel
        else if(action.type == 4) {
            disableDivAction(action.div_action, action.turn_info);
        }
        // wait for results
        else if(action.type == 5) {
            disableDivAction(action.div_action, action.turn_info);
            $("#cancelButton").attr('disabled', true);
            $("#joinButton").attr('disabled', true);
            $("#leaveButton").attr('disabled', true);
        }
        // registration was started
        else if(action.type == 6) {
            message = {};
            message["body"] = messages[0];
            message["from"] = "bot";
            addTextTo("#enTextArea", format_message(message))
        }
        else if(action.type == 7) {
            message = {};
            message["body"] = messages[1];
            message["from"] = "bot";
            addTextTo("#enTextArea", format_message(message))
            $("#joinButton").attr('disabled', true);
            $("#leaveButton").attr('disabled', true);
        }
        else if(action.type == 8) {
            message = {};
            message["body"] = messages[2].f(action.round);
            message["from"] = "bot";
            addTextTo("#enTextArea", format_message(message))
        }
        else if(action.type == 9) {
            message = {};
            message["body"] = messages[3].f(action.round);
            message["from"] = "bot";
            addTextTo("#enTextArea", format_message(message))
        }

        battleBotUpdater.errorSleepTime = 500;
        window.setTimeout(battleBotUpdater.poll, 0);
    },

    onError: function() {
        battleBotUpdater.errorSleepTime *= 2;
        window.setTimeout(battleBotUpdater.poll, battleBotUpdater.errorSleepTime);
    }
};

var updateSkirmishUsers = function(skirmish_users) {
    $("#divSkirmishUsers").empty();
    skirmish_users = String(skirmish_users).split(',');
    if (skirmish_users.length != 0 && skirmish_users[0].length != 0) {
        for (i = 0; i < skirmish_users.length; ++i) {
            $("#divSkirmishUsers").append("<label>+" + skirmish_users[i] + "</label>")
        }
    }

    resize()
};

var showDivAction = function(divAction) {
//    $("#divAction").remove();
    if($("#divAction").length == 0) {
        $("#divMain").append(divAction);
        resize();

        $("#cancelButton").attr('disabled', 'true');

        $("#divAction input[type=text]").keyup(function(){
            value = $(this).val();
            lastChar = value.charAt(value.length - 1);
            if(lastChar > '9' || lastChar < '0') {
                $(this).val(value.substring(0, value.length - 1))
            }
        });

        $("#divAction input[type=text]").change(function(){
            if(!checkTurnSum($(this))) {
                window.alert("Incorrect percentage of the action. Incorrect values were changed to 0");
            }
        });

        $("#resetButton").click(resetButtonClick);

        $("#doButton").click(doButtonClick);

        $("#cancelButton").click(cancelButtonClick);
    }
    $("#divAction *").removeAttr('disabled');
    $("#cancelButton").attr('disabled', true);
};

var disableDivAction = function(divAction, turn_info) {
    if($("#divAction").length == 0) {
        showDivAction(divAction);
    }
    $("#divAction *").attr('disabled', true);
    $("#cancelButton").removeAttr('disabled');
};

/*
    Return true if all values (text inputs in div with id "divAction") are correct (integer), false otherwise
 */
var checkTurnSum = function(element) {
    result = true;
    value = element.val();
    if(!isNaN(value)) {
        var sum = 0;
        i = 0;
        $("#divAction input[type=text]").each(function() {
            intVal = parseInt($(this).val());
            if(isNaN(intVal)) {
                $(this).val("0");
                result = false;
            }
            else {
                $(this).val(intVal);
                sum += intVal;
            }
            ++i;
        });
        if(sum > 100) {
            element.val(value - (sum - 100));
        }
    }
    else {
        element.val("0");
        result = false;
    }

    return result;
};

var removeDivAction = function(divAction) {
    $("#divAction").remove();
    resize()
};

var doButtonClick = function() {
    if(!checkTurnSum($(this))) {
        window.alert("Incorrect percentage of the action. Incorrect values were changed to 0");
    }
    else {
        /*
            Prepare turn information:
            <action1>:<player1>:[<spell1>]:<percent1>,<action2>:<player2>:[<spell2>]:<percent2>,...
         */
        turnInfo = "";
        $(".action").each(function() {
            turnInfo += $(this).attr("action") + ":";
            value = $(".user_select option:selected", this).html();
            turnInfo += ((value) ? value : "") + ":";
            value = $(".spell_select option:selected", this).html();
            turnInfo += ((value) ? value : "") + ":";
            turnInfo += $("input[type=text]", this).val();
            turnInfo += ",";
        });
        $.postJSON('/bot/battle', {'action' : 'turn do', 'turn_info' : turnInfo}, function(){
        });
    }
}

var cancelButtonClick = function() {
    $.postJSON('/bot/battle', {'action' : 'turn cancel'}, function(){
    });
}

var resetButtonClick = function() {
    $("#divAction input[type=text]").each(function() {
        $(this).val("0")
    });
}