/**
 * Author: Pavel Padinker
 * Date: 17.04.12
 * Time: 11:00
 */

var initialize = function () {
    initialize_battle();
    messager.poll();
    onlineUsersUpdater.poll();
    battleBotUpdater.poll();
    characterInfoUpdater.poll();

    width = $("#sideBar").width();
    $("#contentDiv").css('left', width + 5 + 'px');

    showBattle();
    $("#battleAnchor").click(showBattle);
    $("#characterAnchor").click(showCharacter);
    $("#teamAnchor").click(showTeam);
};

var showBattle = function() {
    $("#battleDivContainer").show();
    $("#battleAnchor").parent().attr("class", "active");
    $("#characterDivContainer").hide();
    $("#characterAnchor").parent().removeAttr("class");
    $("#teamDivContainer").hide();
    $("#teamAnchor").parent().removeAttr("class");
};

var showCharacter = function() {
    $("#characterDivContainer").show();
    $("#characterAnchor").parent().attr("class", "active");
    $("#battleDivContainer").hide();
    $("#battleAnchor").parent().removeAttr("class");
    $("#teamDivContainer").hide();
    $("#teamAnchor").parent().removeAttr("class");
};

var showTeam = function() {
    $("#teamDivContainer").show();
    $("#teamAnchor").parent().attr("class", "active");
    $("#battleDivContainer").hide();
    $("#battleAnchor").parent().removeAttr("class");
    $("#characterDivContainer").hide();
    $("#characterAnchor").parent().removeAttr("class");
};

var characterInfoUpdater = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/info/poll', {}, characterInfoUpdater.onSuccess, characterInfoUpdater.onError);
    },

    onSuccess: function(response) {
        var action = $.parseJSON(response);
        // character info update
        if (action.type == 0) {
            var characterInfo = action.character_info.split(":");
            $("#nameLabel").text(characterInfo[0]);
            $("#classLabel").text(characterInfo[1]);
            $("#levelLabel").text(characterInfo[2]);
            $("#HPLabel").text(characterInfo[3]);
            $("#MPLabel").text(characterInfo[4]);
            $("#strengthLabel").text(characterInfo[5]);
            $("#dexterityLabel").text(characterInfo[6]);
            $("#intellectLabel").text(characterInfo[7]);
            $("#wisdomLabel").text(characterInfo[8]);
            $("#expLabel").text(characterInfo[9]);
            $("#goldLabel").text(characterInfo[10]);
            $("#teamLabel").text(characterInfo[11]);
            $("#rankLabel").text(characterInfo[12]);

            $("#nameLabel_battle").text(characterInfo[0]);
            $("#classLabel_battle").text(characterInfo[1]);
            $("#levelLabel_battle").text(characterInfo[2]);
            $("#HPLabel_battle").text(characterInfo[3]);
            $("#MPLabel_battle").text(characterInfo[4]);
        }
        // show create team div
        else if (action.type == 1) {
            $("#teamDivContainer").empty();
            $("#teamDivContainer").append(action.team_div);
            initialize_create_team();
        }
        // show team info div
        else if (action.type == 2) {
            $("#teamDivContainer").empty();
            $("#teamDivContainer").append(action.team_div);
            initialize_team_info();
        }
        // add invitation
        else if (action.type == 3) {
            $("#divInvitationContent").empty();
            $("#divInvitationContent").append(action.invitation_div);
            initialize_team_invitation(action.user_name, action.team_name);
        }

        characterInfoUpdater.errorSleepTime = 500;
        window.setTimeout(characterInfoUpdater.poll, 0);
    },

    onError: function() {
        characterInfoUpdater.errorSleepTime *= 2;
        window.setTimeout(characterInfoUpdater.poll, characterInfoUpdater.errorSleepTime);
    }
};

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
        action = $.parseJSON(response);
        if(action.type == 0) {
            initialOnlineUsers(action.users);
        }
        else if(action.type == 1) {
            addOnlineUser(action.user);
        }
        else if(action.type == 2) {
            removeOnlineUser(action.user);
        }
        // initial skirmish users
        else if(action.type == 3) {
            initialSkirmishUsers(action.skirmish_users);
        }
        // add skirmish user
        else if(action.type == 4) {
            addSkirmishUser(action.skirmish_user);
        }
        // remove skirmish user
        else if(action.type == 5) {
            removeSkirmishUser(action.skirmish_user);
        }

        onlineUsersUpdater.errorSleepTime = 500;
        window.setTimeout(onlineUsersUpdater.poll, 0);
    },

    onError: function() {
        onlineUsersUpdater.errorSleepTime *= 2;
        window.setTimeout(onlineUsersUpdater.poll, onlineUsersUpdater.errorSleepTime);
    }
};

var battleBotUpdater = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/bot/poll', {}, battleBotUpdater.onSuccess, battleBotUpdater.onError);
    },

    onSuccess: function(response) {
        var action = $.parseJSON(response);
        // can join
        if(action.type == 3) {
            $("#joinButton").removeAttr('disabled');
            $("#joinButton").show();
            $("#leaveButton").hide();
        }
        // can leave
        else if(action.type == 4) {
            $("#leaveButton").show();
            $("#leaveButton").removeAttr('disabled');
            $("#joinButton").hide();
        }
        // can do turn
        else if(action.type == 5) {
            removeDivAction();
            showDivAction(action.div_action);
        }
        // can cancel
        else if(action.type == 6) {
            disableDivAction(action.div_action, action.turn_info);
        }
        // wait for results
        else if(action.type == 7) {
            disableDivAction(action.div_action, action.turn_info);
            $("#cancelButton").attr('disabled', true);
        }
        // reset to initial
        else if(action.type == 8) {
            removeDivAction();
            $("#joinButton").attr('disabled', true);
            $("#leaveButton").attr('disabled', true);
        }
        // message action
        else if(action.type == 9) {
            message = {};
            if(action.message_number == 2 || action.message_number == 3)
            {
                message["body"] = messages[action.message_number].f(action.round);
            }
            else
            {
                message["body"] = messages[action.message_number];
            }
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

var initialOnlineUsers = function(users) {
    var online_users = String(users).split(',');
    online_users.sort();
    $("#divOnlineUsers").empty();
    for (i = 0; i < online_users.length; ++i) {
        $("#divOnlineUsers").append("<label value=\"" + online_users[i] + "\">" + online_users[i] + "</label>")
    }

    resize_battle();
};

var removeOnlineUser = function(user) {
    $("#divOnlineUsers label[value=\"" + user + "\"]").remove();
    $("#inviteUserSelect option[value=\"" + user + "\"]").remove();

    resize_battle();
};

var addOnlineUser = function(user) {
    inserted = false;
    // insert after specified element
    $("#divOnlineUsers label").each(function(){
        if (!inserted && ($(this).text() > user)) {
            $(this).before("<label value=\"" + user + "\">" + user + "</label>");
            inserted = true;
        }
    });
    if (!inserted) {
        $("#divOnlineUsers").append("<label value=\"" + user + "\">" + user + "</label>");
        $("#inviteUserSelect").append("<option value=\"" + user + "\">" + user + "</option>");
    }
    else{
        $("#inviteUserSelect option").each(function(){
            if ($(this).text() > user) {
                $(this).before("<option value=\"" + user + "\">" + user + "</option>");
            }
        });
    }

    resize_battle();
};

var initialSkirmishUsers = function(users) {
    if (users) {
        var skirmish_users = String(users).split(',');
        skirmish_users.sort();
        $("#divSkirmishUsers").empty();
        for (i = 0; i < skirmish_users.length; ++i) {
            $("#divSkirmishUsers").append("<label value=\"" + skirmish_users[i] + "\">" + skirmish_users[i] + "</label>")
        }

        resize_battle();
    }
};

var removeSkirmishUser = function(user) {
    $("#divSkirmishUsers label[value=\"" + user + "\"]").remove();

    resize_battle();
};

var addSkirmishUser = function(user) {
    inserted = false;
    // insert after specified element
    $("#divSkirmishUsers label").each(function(){
        if ($(this).text() > user) {
            $(this).before("<label value=\"" + user + "\">" + user + "</label>");
            inserted = true;
        }
    });
    if (!inserted) {
        $("#divSkirmishUsers").append("<label value=\"" + user + "\">" + user + "</label>");
    }

    resize_battle();
};

