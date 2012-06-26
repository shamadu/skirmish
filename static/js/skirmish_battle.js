/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 13:40
 */

var initialize_battle = function () {
    $("#dropButton").click(dropButtonClick);
    $("#sendButton").click(sendFunc);
    $("#sendTextArea").keypress(keyPress);
    $("#joinButton").attr('disabled', true);
    $("#leaveButton").attr('disabled', true);
    $("#leaveButton").hide();
    $("#joinButton").click(joinButtonClick);
    $("#leaveButton").click(leaveButtonClick);

    $("#locationSelect").change(changeLocationFunc);
    onChangeLocation();

    window.blinker = setInterval(function() {
        $(".blink").animate({opacity:0.5},500,"linear",function(){
            $(this).animate({opacity:1},500);
        });
    }, 1000);
};

var onChangeLocation = function() {
    location_name = $("#locationSelect option:selected").html();
    $("#locationTab").html(location_name);
    $("#locationTextArea").html("");
    message = {};
    message["body"] = messages[2].format(location_name);
    element = $("#battleTextArea");
    element.html(format_message(message));
    element.animate({ scrollTop: element.prop("scrollHeight") - element.height() }, 100);
};

var changeLocationFunc = function() {
    removeDivAction();
    $.postJSON('/action', {"action" : "change_location", "location" : $("option:selected", this).val()}, function() {
        onChangeLocation()
    });
};

var dropButtonClick = function () {
    $.postJSON('/action', {"action" : "drop"}, function() {
        window.location.href='/';
    });
};

var joinButtonClick = function () {
    $.postJSON('/action', {'action' : 'join'}, function() {
    });
};

var leaveButtonClick = function () {
    $.postJSON('/action', {'action' : 'leave'}, function() {
    });
};

var resize_battle = function() {
    width = $("#divActionContainer").width();
    if (width != 0) {
        $("#divChat").css('right', width + 15 + 'px');
    }
    else {
        $("#divChat").css('right', 0);
    }
};

var sendFunc = function() {
    data = {
        "action" : "new_message",
        'body' : $("#sendTextArea").val(),
        'message_type' : 'location'
    };
    $("#sendTextArea").val("");
    $("#sendTextArea").focus();

    if (!$("#tabChat li.active").hasClass("mainTab")) {
        data["message_type"] = "private";
        data["to"] = $("#tabChat li.active >a>span").html();
    }
    else if($("#tabChat li.active>a").attr("id") == "teamTab") {
        data["message_type"] = "team";
    }

    $.postJSON('/action', data, function() {
    });
};

var keyPress = function(event) {
    // mozilla has 13 key for enter with/without ctrl, chrome and IE
    // have 10 key if enter is pressed with ctrl
    if ((event.which == 10 || event.which == 13 )) {
        if(event.ctrlKey) {
            $("#sendTextArea").val($("#sendTextArea").val() + "\n");
            //browserIsIE
            if (this.createTextRange) {
                var range = this.createTextRange();
                range.collapse(false);
                range.select();
            }
            else {
                $("#sendTextArea").focus();
                $("#sendTextArea").animate({ scrollTop: $("#sendTextArea").prop("scrollHeight") - $("#sendTextArea").height() }, 0);
            }
        }
        else {
            event.preventDefault();
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
        message_formatted += "[" + hours + ":" + minutes + ":" + seconds + "]"
        if (message.from) {
            message_formatted += "[" + message.from + "]:"
        }

        message_formatted += " " + body_lines[line] + "<br>";
    }

    return message_formatted;
};

var format_private_message = function(message, income) {
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
        message_formatted += "[" + hours + ":" + minutes + ":" + seconds + "]"
        if (income) {
            message_formatted += "<<:"
        }
        else {
            message_formatted += ">>:"
        }

        message_formatted += " " + body_lines[line] + "<br>";
    }

    return message_formatted;
};

var addTextTo = function(tab_element_id, message) {
    tab_element = $(tab_element_id);
    if (!tab_element.parent().hasClass("active"))
    {
        tab_element.addClass("blink");
    }
    element = $(">div", tab_element.attr("href"));
    element.html(element.html() + message);
    element.animate({ scrollTop: element.prop("scrollHeight") - element.height() }, 100);
};

var addDivAction = function(divAction) {
    $("#divActionContainer").append(divAction);
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

    $("#divAction select.spell_select").change(function(){
        if($("option:selected", this).hasClass("self")) {
            $(".user_select option[value=\"" + $("#nameLabel").text() + "\"]", $(this).parent()).attr("selected", "selected");
            $(".user_select", $(this).parent()).attr('disabled', 'true');
        }
        else {
            $(".user_select", $(this).parent()).removeAttr('disabled');
        }
    });

    $("#resetButton").click(resetButtonClick);

    $("#doButton").click(doButtonClick);

    $("#cancelButton").click(cancelButtonClick);

    height = $("#divAction").height();
    $("#divAction").height(1);
    $("#divAction").animate({ height: height }, 1000, function() {
//        resize_battle();
    });
};

var enableDivAction = function() {
    $("#divAction input,#divAction select,#divAction button").removeAttr('disabled');
    $("#cancelButton").attr('disabled', true);
};

var showTurnInfo = function(turn_info) {
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
    $("#divAction").animate({ height: 0 }, 1000, function() {
        $("#divAction").remove();
        resize_battle()
    });
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
            $.postJSON('/action', {'action' : 'turn_do', 'turn_info' : turnInfo}, function(){
            });
        }
        else {
            window.alert(messages[1])
        }
    }
};

var cancelButtonClick = function() {
    $.postJSON('/action', {'action' : 'turn_cancel'}, function(){
    });
};

var resetButtonClick = function() {
    $("#divAction input[type=text]").each(function() {
        $(this).val("0")
    });
};