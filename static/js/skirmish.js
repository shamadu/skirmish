/**
 * Author: Pavel Padinker
 * Date: 17.04.12
 * Time: 11:00
 */

var initialize = function () {
    initialize_battle();
    initialize_character();
    initialize_shop();
    initialize_DB();
    messager.poll();
    pollUpdater.poll();

    width = $("#sideBar").width();
    $("#contentDiv").css('left', width + 10 + 'px');

    showBattle();
    $("#battleAnchor").click(showBattle);
    $("#characterAnchor").click(showCharacter);
    $("#teamAnchor").click(showTeam);
    $("#shopAnchor").click(showShop);
    $("#dbAnchor").click(showDB);
};

var showBattle = function() {
    $("#contentDiv >div.contentDiv").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#battleDivContainer").show();
    $("#battleAnchor").parent().attr("class", "active");
    resize_battle();
};

var showCharacter = function() {
    $("#contentDiv >div.contentDiv").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#characterDivContainer").show();
    $("#characterAnchor").parent().attr("class", "active");
};

var showTeam = function() {
    $("#contentDiv >div.contentDiv").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#teamDivContainer").show();
    $("#teamAnchor").parent().attr("class", "active");
};

var showShop = function() {
    $("#contentDiv >div.contentDiv").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#shopDivContainer").show();
    $("#shopAnchor").parent().attr("class", "active");
};

var showDB = function() {
    $("#contentDiv >div.contentDiv").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#dbDivContainer").show();
    $("#dbAnchor").parent().attr("class", "active");
};

var messager = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/message/poll', {}, messager.onSuccess, messager.onError);
    },

    onSuccess: function(response) {
        var message = $.parseJSON(response);
        if(message.to == "all") {
            addTextTo($("#tabChat >div>div.active>div"), format_message(message))
        }

        messager.errorSleepTime = 500;
        window.setTimeout(messager.poll, 0);
        $("#serverStatus").html("Connected");
    },

    onError: function() {
        $("#serverStatus").html("Disconnected");
        messager.errorSleepTime *= 2;
        window.setTimeout(messager.poll, messager.errorSleepTime);
    }
};

var createOnlineUserLabel = function(user_name) {
    return "<label value=\"" + user_name + "\">" + user_name + "</label>";
};

var initialOnlineUsers = function(users) {
    $("#divOnlineUsers").empty();
    var online_users = String(users).split(',');
    online_users.sort();
    for (i = 0; i < online_users.length && online_users[i]; ++i) {
        pollUpdater.online_users.push(online_users[i]);
        $("#divOnlineUsers").append(createOnlineUserLabel(online_users[i]));
        $("#inviteUserSelect").append("<option value=\"" + online_users[i] + "\">" + online_users[i] + "</option>");
    }
    resize_battle();
};

var removeOnlineUser = function(user, fromServer) {
    $("#divOnlineUsers label[value=\"" + user + "\"]").remove();
    $("#inviteUserSelect option[value=\"" + user + "\"]").remove();
    if($("#inviteUserSelect option").length == 0) {
        $("#inviteDiv").hide();
    }

    if (fromServer) {
        pollUpdater.online_users.pop(user);
        resize_battle();
    }
};

var addOnlineUser = function(user, fromServer) {
    inserted = false;
    // insert after specified element
    $("#divOnlineUsers label").each(function(){
        if (!inserted && ($(this).text() > user)) {
            $(this).before(createOnlineUserLabel(user));
            inserted = true;
        }
    });
    if (!inserted) {
        $("#divOnlineUsers").append(createOnlineUserLabel(user));
        $("#inviteUserSelect").append("<option value=\"" + user + "\">" + user + "</option>");
    }
    else{
        $("#inviteUserSelect option").each(function(){
            if ($(this).text() > user) {
                $(this).before("<option value=\"" + user + "\">" + user + "</option>");
            }
        });
    }

    $("#inviteDiv").show();
    if (fromServer) {
        pollUpdater.online_users.push(user);
        resize_battle();
    }
};

var createSkirmishUserLabel = function(user_name, team_name) {
    if (team_name) {
        return "<label value=\"" + user_name + "\" style=\"color:red\">" + user_name + "[" + team_name + "]</label>";
    }
    else {
        return "<label value=\"" + user_name + "\" style=\"color:red\">" + user_name + "</label>";
    }
};

var initialSkirmishUsers = function(users) {
    $("#divSkirmishUsers").empty();
    if (users) {
        var skirmish_users = String(users).split(',');
        skirmish_users.sort();
        for (i = 0; i < skirmish_users.length && skirmish_users[i]; ++i) {
            skirmish_user = skirmish_users[i].split(":");
            pollUpdater.online_users.push(skirmish_user[0]);
            $("#divSkirmishUsers").append(createSkirmishUserLabel(skirmish_user[0], skirmish_user[1]))
        }

        resize_battle();
    }
};

var removeSkirmishUser = function(user) {
    skirmish_user = user.split(":");
    $("#divSkirmishUsers label[value=\"" + skirmish_user[0] + "\"]").remove();
    if (-1 != $.inArray(skirmish_user[0], pollUpdater.online_users)){
        addOnlineUser(skirmish_user[0], false);
    }

    resize_battle();
};

var addSkirmishUser = function(user) {
    skirmish_user = user.split(":");
    removeOnlineUser(skirmish_user[0], false);
    inserted = false;
    // insert after specified element
    $("#divSkirmishUsers label").each(function(){
        if ($(this).text() > user) {
            $(this).before(createSkirmishUserLabel(skirmish_user[0], skirmish_user[1]));
            inserted = true;
        }
    });
    if (!inserted) {
        $("#divSkirmishUsers").append(createSkirmishUserLabel(skirmish_user[0], skirmish_user[1]));
    }

    resize_battle();
};

var pollUpdater = {
    errorSleepTime: 500,
    online_users : new Array(),

    poll: function() {
        $.postJSON('/poll', {}, pollUpdater.onSuccess, pollUpdater.onError);
    },

    onSuccess: function(response) {
        var action = $.parseJSON(response);
        // add turn div
        if(action.type == 1) {
            addDivAction(action.div_action);
        }
        // set skirmish users
        else if(action.type == 2) {
            $("#divAction .user_select").each(function(){
               $(this).empty();
                for (i = 0; i < action.skirmish_users.length; ++i){
                    $(this).append("<option value=\"" + action.skirmish_users[i] + "\">" + action.skirmish_users[i] + "</option>");
                }
            });
        }
        // can join
        else if(action.type == 3) {
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
            enableDivAction();
            if (action.turn_info) {
                showTurnInfo(action.turn_info);
            }
            // set self spells
            $("#divAction select.spell_select option:selected").each(function(){
                if($(this).hasClass("self")) {
                    $(".user_select option[value=\"" + $("#nameLabel_battle").text() + "\"]", $(this).parent().parent()).attr("selected", "selected");
                    $(".user_select", $(this).parent().parent()).attr('disabled', 'true');
                }
            });
        }
        // can cancel
        else if(action.type == 6) {
            disableDivAction();
            if (action.turn_info) {
                showTurnInfo(action.turn_info);
            }
        }
        // wait for results
        else if(action.type == 7) {
            disableDivAction();
            $("#cancelButton").attr('disabled', true);
            if (action.turn_info) {
                showTurnInfo(action.turn_info);
            }
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
            message["body"] = action.battle_message;
            message["from"] = "bot";
            addTextTo("#tabChat >div>div.active>div", format_message(message))
        }
        // add skirmish user
        else if(action.type == 10) {
            addSkirmishUser(action.skirmish_user);
        }
        // remove skirmish user
        else if(action.type == 11) {
            removeSkirmishUser(action.skirmish_user);
        }
        else if(action.type == 100) {
            pollUpdater.online_users.length = 0;
            initialOnlineUsers(action.online_users);
            initialSkirmishUsers(action.skirmish_users);
        }
        else if(action.type == 101) {
            addOnlineUser(action.user, true);
        }
        else if(action.type == 102) {
            removeOnlineUser(action.user, true);
        }
        // character info update
        else if (action.type == 200) {
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
            $("#constitutionLabel").text(characterInfo[9]);
            $("#attackLabel").text(characterInfo[10]);
            $("#defenceLabel").text(characterInfo[11]);
            $("#magicAttackLabel").text(characterInfo[12]);
            $("#magicDefenceLabel").text(characterInfo[13]);
            $("#armorLabel").text(characterInfo[14]);
            $("#experienceLabel").text(characterInfo[15]);
            $("#goldLabel").text(characterInfo[16]);
            $("#teamLabel").text(characterInfo[17]);
            $("#rankLabel").text(characterInfo[18]);

            $("#nameLabel_battle").text(characterInfo[0]);
            $("#classLabel_battle").text(characterInfo[1]);
            $("#levelLabel_battle").text(characterInfo[2]);
            $("#HPLabel_battle").text(characterInfo[3]);
            $("#MPLabel_battle").text(characterInfo[4]);
        }
        // character stuff update
        else if (action.type == 201) {
            if (action.weapon) {
                $("#weaponSelect").empty();
                addThings(action.weapon, $("#weaponSelect"));
            }
            if (action.shield) {
                addThings(action.shield, $("#shieldSelect"));
            }
            if (action.head) {
                addThings(action.head, $("#headSelect"));
            }
            if (action.body) {
                addThings(action.body, $("#bodySelect"));
            }
            if (action.left_hand) {
                addThings(action.left_hand, $("#left_handSelect"));
            }
            if (action.right_hand) {
                addThings(action.right_hand, $("#right_handSelect"));
            }
            if (action.legs) {
                addThings(action.legs, $("#legsSelect"));
            }
            if (action.feet) {
                addThings(action.feet, $("#feetSelect"));
            }
            if (action.cloak) {
                addThings(action.cloak, $("#cloakSelect"));
            }
        }
        // character spells update
        else if (action.type == 202) {
            $("#characterSpellDiv").empty();
            $("#characterSpellDiv").append(action.spells_div);
            $("#learnSpellTable button").click(learnSpellFunc);
        }
        // show create team div
        else if (action.type == 203) {
            $("#teamDivContainer").empty();
            $("#teamDivContainer").append(action.team_div);
            initialize_create_team();
        }
        // show team info div
        else if (action.type == 204) {
            $("#teamDivContainer").empty();
            $("#teamDivContainer").append(action.team_div);
            initialize_team_info();
        }
        // add invitation
        else if (action.type == 205) {
            $("#divInvitationContent").empty();
            $("#divInvitationContent").append(action.invitation_div);
            initialize_team_invitation(action.user_name, action.team_name);
        }

        pollUpdater.errorSleepTime = 500;
        window.setTimeout(pollUpdater.poll, 0);
    },

    onError: function() {
        pollUpdater.errorSleepTime *= 2;
        window.setTimeout(pollUpdater.poll, pollUpdater.errorSleepTime);
    }
};
