/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 13:40
 */

var initialize_battle = function () {
    $("#logoutButton").click(logoutFunc);
    $("#dropButton").click(dropButtonClick);
    $("#sendButton").click(sendFunc);
    $("#sendTextArea").keypress(keyPress);
    $("#joinButton").attr('disabled', true);
    $("#leaveButton").attr('disabled', true);
    $("#leaveButton").hide();
    $("#joinButton").click(joinButtonClick);
    $("#leaveButton").click(leaveButtonClick);

    $('a[data-toggle="tab"]').on('shown', function (tab) {
        removeDivAction();
        $.postJSON('/character', {"action" : "change_location", "location" : $(this).html()}, function() {
        });
    });
};

var dropButtonClick = function () {
    $.postJSON('/character', {"action" : "drop"}, function() {
        window.location.href='/';
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

var resize_battle = function() {
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
    element = $(element_id);
    element.val(element.val() + message);
    element.scrollTop(element[0].scrollHeight - element.height());
};

var showDivAction = function(divAction, turn_info) {
    if($("#divAction").length == 0) {
        $("#divMain").append(divAction);
        resize_battle();

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
    $("#divAction input,#divAction select,#divAction button").removeAttr('disabled');
    $("#cancelButton").attr('disabled', true);

    if (turn_info) {
        turn_infos = turn_info.split(",");
        attack_count = 0;
        defence_count = 0;
        spell_count = 0;
        for (i = 0; i < turn_infos.length; i++){
            if (turn_infos[i]) {
                turn_parts = turn_infos[i].split(":");
                if (turn_parts[0] == 0) {
                    div = $("#divAction .action[action='0']")[attack_count];
                    attack_count += 1;
                }
                else if (turn_parts[0] == 1) {
                    div = $("#divAction .action[action='1']")[defence_count];
                    defence_count += 1;
                }
                else if (turn_parts[0] == 2) {
                    div = $("#divAction .action[action='2']")[spell_count];
                    spell_count += 1;
                }
                else if (turn_parts[0] == 3) {
                    div = $("#divAction .action[action='3']");
                }
                // if there is target user_name and there is such user in list, restore turn part
                // if there is no such user - do nothing
                if (turn_parts[1] ) {
                    if ($(".user_select option[value=\"" + turn_parts[1] + "\"]", $(div)).length > 0) {
                        $(".user_select option[value=\"" + turn_parts[1] + "\"]", $(div)).attr("selected", "selected");
                        if (turn_parts[2]) {
                            $(".spell_select option[value=\"" + turn_parts[2] + "\"]", $(div)).attr("selected", "selected");
                        }
                        $("input", $(div)).val(turn_parts[3]);
                    }
                }
                // if there is no target user - restore turn
                else {
                    if (turn_parts[2]) {
                        $(".spell_select option[value=\"" + turn_parts[2] + "\"]", $(div)).attr("selected", "selected");
                    }
                    $("input", $(div)).val(turn_parts[3]);
                }
            }
        }
    }
};


var disableDivAction = function(divAction, turn_info) {
    if($("#divAction").length == 0) {
        showDivAction(divAction, turn_info);
    }
    $("#divAction input,#divAction select,#divAction button").attr('disabled', true);
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
    resize_battle()
};

var doButtonClick = function() {
    if(!checkTurnSum($(this))) {
        window.alert(messages[0]);
    }
    else {
        /*
         Prepare turn information:
         <action1>:<player1>:[<spell1>]:<percent1>,<action2>:<player2>:[<spell2>]:<percent2>,...
         */
        turnInfo = "";
        $(".action").each(function() {
            percent = $("input[type=text]", this).val();
            if (percent != 0) {
                turnInfo += $(this).attr("action") + ":";
                value = $(".user_select option:selected", this).html();
                turnInfo += ((value) ? value : "") + ":";
                value = $(".spell_select option:selected", this).val();
                turnInfo += ((value) ? value : "") + ":";
                turnInfo += $("input[type=text]", this).val();
                turnInfo += ",";
            }
        });
        if (turnInfo) {
            $.postJSON('/bot/battle', {'action' : 'turn do', 'turn_info' : turnInfo}, function(){
            });
        }
        else {
            window.alert(messages[1])
        }
    }
};

var cancelButtonClick = function() {
    $.postJSON('/bot/battle', {'action' : 'turn cancel'}, function(){
    });
};

var resetButtonClick = function() {
    $("#divAction input[type=text]").each(function() {
        $(this).val("0")
    });
};