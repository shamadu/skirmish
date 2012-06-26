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
    pollUpdater.poll();

    width = $("#sideBar").width();
    $("#contentDiv").css('left', width + 10 + 'px');

    showBattle();
    $("#battleAnchor").click(showBattle);
    $("#characterAnchor").click(showCharacter);
    $("#teamAnchor").click(showTeam);
    $("#shopAnchor").click(showShop);
    $("#dbAnchor").click(showDB);
    $("#logoutAnchor").click(logoutFunc);

    // hide menu if opened
    $(document.body).click(function(){
       if ($(".vmenu :visible")) {
           $('.vmenu').hide();
       }
    });
    // initialize right click user context menu
    $('.vmenu .first_li').live('click',function() {
        $('.vmenu').hide();
    });

    $(".first_li").hover(function () {
                $(this).css({backgroundColor : '#EEE'});
            },
            function () {
                $(this).css('background-color' , '#FFF' );
            });

    $("#divOnlineUsers label").live({
        mouseenter : function () {
            $(this).css({backgroundColor : '#EEE'});
        },
        mouseleave : function () {
            $(this).css('background-color' , '#FFF' );
        },
        contextmenu : function(e){
            left_offset = e.pageX + 1;
            if (document.width - e.pageX < $("#vmenu").width()) {
                left_offset = document.width - $("#vmenu").width() - 10;
            }
            // add info about user name to context menu to use it in menu items
            $("#vmenu").data("user_name", $(this).attr('value'));
            $("#vmenu").css({ left: left_offset, top: e.pageY + 1, zIndex: '101' }).show();
            return false;
        },
        click : function() {
            $("#vmenu").data("user_name", $(this).attr('value'));
            openPrivateChatFunc();
        }
    });

    $("#inviteMenuItem").click(inviteToTeamFunc);
    $("#privateChatMenuItem").click(openPrivateChatFunc);

    // store previous tab to use if close event is called
    $('#tabChat a[data-toggle="tab"]').live('shown', function (e) {
        // stop blinking if blinking (there has been new unread message)
        if ($(this).hasClass("blink"))
        {
            $(this).removeClass("blink");
        }
        // go to the end of chat
        element = $(">div", $(this).attr("href"));
        element.animate({ scrollTop: element.prop("scrollHeight") - element.height() }, 100);
        // save previous tab to return to it if this on would be closed
        $("#tabChat").data("previousTab", e.relatedTarget);
        $("#sendTextArea").focus();
    });

    $(".tabClose").live('click', closePrivateChatFunc);
};

var showBattle = function() {
    $("#contentDiv >div.div-content").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#battleDivContainer").show();
    $("#battleAnchor").parent().attr("class", "active");
    resize_battle();
};

var showCharacter = function() {
    $("#contentDiv >div.div-content").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#characterDivContainer").show();
    $("#characterAnchor").parent().attr("class", "active");
};

var showTeam = function() {
    $("#contentDiv >div.div-content").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#teamDivContainer").show();
    $("#teamAnchor").parent().attr("class", "active");
};

var showShop = function() {
    $("#contentDiv >div.div-content").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#shopDivContainer").show();
    $("#shopAnchor").parent().attr("class", "active");
};

var showDB = function() {
    $("#contentDiv >div.div-content").hide();
    $("#sideBar li:not(#serverStatus)").removeAttr("class");
    $("#dbDivContainer").show();
    $("#dbAnchor").parent().attr("class", "active");
};

var inviteToTeamFunc = function() {
    $.postJSON('/action', {"action" : "invite_team", "user_name" : $("#vmenu").data("user_name")}, function(response) {
        var res = $.parseJSON(response);
        window.alert(res.msg);
    });
};

// this function is called from poll handler only. Call openPrivateChatFunc instead
var openPrivateChat = function(userName, message) {
    if ($("#" + userName + "Tab").length == 0) {
        $("#tabChat >ul").append(
                "<li>" +
                        "<a id=\"" + userName + "Tab\" href=\"#" + userName + "Pane\" data-toggle=\"tab\">" +
                        "<span>" + userName + "</span>" +
                        "<button class=\"close tabClose\">&times;</button></a>" +
                        "</li>");
        $("#tabChat >div.tab-content").append(
                "<div class=\"tab-pane\" id=\"" + userName + "Pane\">" +
                        "<div id=\"" + userName + "TextArea\" class=\"text-chat notranslate\"></div>" +
                        "</div>"
        );
        $("#" + userName + "Tab").tab('show');
    }
    addTextTo("#" + userName + "Tab", message)
};

var openPrivateChatFunc = function() {
    $.postJSON('/action', {"action" : "open_chat", "user_name" : $("#vmenu").data("user_name")}, function(response) {
    });
};

var closePrivateChatFunc = function() {
    $.postJSON('/action', {"action" : "close_chat", "user_name" : $(">span", $(this).parent()).html()}, function(response) {
    });
    removeTab($(this).parent());
};

var removeTab = function(tab) {
    // if tab is the same as previous - we are closing active tab, make active next tab
    if ($("#tabChat").data("previousTab")) {
        $($("#tabChat").data("previousTab")).tab('show');
    }
    // we are closing non active tab, restore active (as now active is removed element)
    else {
        $("#tabChat a:first").tab('show');
    }
    // remove pane from content
    $("#tabChat .tab-content " + $(tab).attr("href")).remove();
    // remove this tab from list
    $(tab).parent().remove();
    $("#tabChat").data("previousTab", null);
};

var addTeamChat = function(teamName) {
    if ($("#teamTab").length == 0) {
        $("<li class=\"mainTab\">" +
                "<a id=\"teamTab\" href=\"#teamPane\" data-toggle=\"tab\">" +
                "<span>" + teamName + "</span>" +
                "</li>").insertAfter($("#tabChat #locationTab").parent());
        $("<div class=\"tab-pane\" id=\"teamPane\">" +
                "<div id=\"teamTextArea\" class=\"text-chat\"></div>" +
                "</div>").insertAfter("#tabChat #locationPane");
        $("#teamTab").tab('show');
    }
};

var removeTeamChat = function() {
    removeTab($("#teamTab"));
};

var createLocationUserLabel = function(user_name) {
    return "<label class=\"location-user-label\" value=\"" + user_name + "\">" + user_name + "</label>";
};

var createTeamUserLabel = function(user_name) {
    return "<label class=\"location-user-label team-user-label\" value=\"" + user_name + "\">" + user_name + "</label>";
};

var createSkirmishUserLabel = function(user_name, team_name) {
    if (team_name) {
        return "<label class=\"skirmish-user-label\" value=\"" + user_name + "\">" + user_name + "[" + team_name + "]</label>";
    }
    else {
        return "<label class=\"skirmish-user-label\" value=\"" + user_name + "\">" + user_name + "</label>";
    }
};

var initLocationUsers = function(location_users_str, team_users_str, skirmish_users_str) {
    var skirmish_users_names = new Array();
    if (skirmish_users_str) {
        var skirmish_users = String(skirmish_users_str).split(',');
        skirmish_users.sort();
        for (i = 0; i < skirmish_users.length && skirmish_users[i]; ++i) {
            skirmish_user = skirmish_users[i].split(":");
            skirmish_users_names.push(skirmish_user[0]);
            $("#divOnlineUsers").append(createSkirmishUserLabel(skirmish_user[0], skirmish_user[1]))
        }
    }

    if (team_users_str) {
        var team_users = String(team_users_str).split(',');
        team_users.sort();
        for (i = 0; i < team_users.length && team_users[i]; ++i) {
            $("#divOnlineUsers").append(createTeamUserLabel(team_users[i]));
            if (jQuery.inArray(team_users[i], skirmish_users_names) != -1) {
                hideLocationUser(team_users[i]);
            }
        }
    }

    var location_users = String(location_users_str).split(',');
    location_users.sort();

    for (i = 0; i < location_users.length; ++i) {
        $("#divOnlineUsers").append(createLocationUserLabel(location_users[i]));
        if (jQuery.inArray(location_users[i], skirmish_users_names) != -1) {
            hideLocationUser(location_users[i]);
        }
    }
};

var removeLocationUser = function(user) {
    $("#divOnlineUsers .location-user-label[value=\"" + user + "\"]").remove();
};

var addLocationUser = function(user, team_mate) {
    inserted = false;
    if (!team_mate) {
        // insert after specified element
        $(".location-user-label:not(.team-user-label)", $("#divOnlineUsers")).each(function(){
            if (!inserted && ($(this).text() > user)) {
                $(this).before(createLocationUserLabel(user));
                inserted = true;
            }
        });
        if (!inserted) {
            $("#divOnlineUsers").append(createLocationUserLabel(user));
        }
    }
    else {
        // insert after specified element
        $(".team-user-label", $("#divOnlineUsers")).each(function(){
            if (!inserted && ($(this).text() > user)) {
                $(this).before(createTeamUserLabel(user));
                inserted = true;
            }
        });
        if (!inserted) {
            if ($(".team-user-label", $("#divOnlineUsers")).length > 0) { // insert before first online user
                $(createTeamUserLabel(user)).insertBefore(".location-user-label:not(.team-user-label):first", $("#divOnlineUsers"));
            }
            else {
                $("#divOnlineUsers").append(createTeamUserLabel(user));
            }
        }
    }
};

var hideLocationUser = function(user) {
    $("#divOnlineUsers .location-user-label[value=\"" + user + "\"]").hide();
};

var showLocationUser = function(user) {
    $("#divOnlineUsers .location-user-label[value=\"" + user + "\"]").show();
};

var removeSkirmishUser = function(user) {
    skirmish_user = user.split(":");
    $("#divOnlineUsers .skirmish-user-label[value=\"" + skirmish_user[0] + "\"]").remove();
    showLocationUser(skirmish_user[0]);
};

var addSkirmishUser = function(user) {
    skirmish_user = user.split(":");
    hideLocationUser(skirmish_user[0]);
    inserted = false;
    // insert after specified element
    $("#divOnlineUsers .skirmish-user-label").each(function(){
        if ($(this).text() > user) {
            $(this).before(createSkirmishUserLabel(skirmish_user[0], skirmish_user[1]));
            inserted = true;
        }
    });
    if (!inserted) {
        $("#divOnlineUsers").prepend(createSkirmishUserLabel(skirmish_user[0], skirmish_user[1]));
    }
};

var initialTeamUsers = function(users) {
    if (users) {
        var team_users = String(users).split(',');
        team_users.sort();
        for (i = 0; i < team_users.length && team_users[i]; ++i) {
            $("#divOnlineUsers").append(createTeamUserLabel(team_users[i]));
        }
    }
};

var removeTeamUser = function(user) {
    $("#divOnlineUsers .team-user-label[value=\"" + user + "\"]").remove();
};

var addTeamUser = function(user) {
    inserted = false;
    // insert after specified element
    $(".team-user-label", $("#divOnlineUsers")).each(function(){
        if (!inserted && ($(this).text() > user)) {
            $(this).before(createTeamUserLabel(user));
            inserted = true;
        }
    });
    if (!inserted) {
        if ($(".location-user-label", $("#divOnlineUsers")).length > 0) { // insert before first online user
            $(createTeamUserLabel(user)).insertBefore(".location-user-label:first", $("#divOnlineUsers"));
        }
        else {
            $("#divOnlineUsers").append(createTeamUserLabel(user));
        }
    }
};

var pollUpdater = {
    errorSleepTime: 500,

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
            resize_battle();
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
                    $(".user_select option[value=\"" + $("#nameLabel").text() + "\"]", $(this).parent().parent()).attr("selected", "selected");
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
            addTextTo("#battleTab", format_message(message))
        }
        // add skirmish user
        else if(action.type == 10) {
            addSkirmishUser(action.skirmish_user);
            resize_battle();
        }
        // remove skirmish user
        else if(action.type == 11) {
            removeSkirmishUser(action.skirmish_user);
            resize_battle();
        }
        else if(action.type == 100) {
            $("#divOnlineUsers").empty();
            initLocationUsers(action.location_users, action.team_users, action.skirmish_users);
            resize_battle();
        }
        else if(action.type == 101) {
            addLocationUser(action.user, action.team_mate);
            resize_battle();
        }
        else if(action.type == 102) {
            removeLocationUser(action.user);
            resize_battle();
        }
        else if(action.type == 103) {
            openPrivateChat(action.user, action.message);
        }
        else if(action.type == 104) {
//            addTeamUser(action.user);
            resize_battle();
        }
        else if(action.type == 105) {
//            removeTeamUser(action.user);
            resize_battle();
        }
        // character info update
        else if (action.type == 200) {
            var characterInfo = action.character_info.split(":");
            $("#nameLabel").text(characterInfo[0]);
            $("#raceLabel").text(characterInfo[1]);
            $("#classLabel").text(characterInfo[2]);
            $("#levelLabel").text(characterInfo[3]);
            $("#strengthLabel").text(characterInfo[6]);
            $("#dexterityLabel").text(characterInfo[7]);
            $("#intellectLabel").text(characterInfo[8]);
            $("#wisdomLabel").text(characterInfo[9]);
            $("#constitutionLabel").text(characterInfo[10]);
            $("#attackLabel").text(characterInfo[11]);
            $("#defenceLabel").text(characterInfo[12]);
            $("#magicAttackLabel").text(characterInfo[13]);
            $("#magicDefenceLabel").text(characterInfo[14]);
            $("#armorLabel").text(characterInfo[15]);
            $("#goldLabel").text(characterInfo[18]);
            if (characterInfo[19]){
                $("#teamLabel").text(characterInfo[19]);
                $("#rankLabel").text(characterInfo[20]);
                if (characterInfo[20] > 1) {
                    $("#inviteMenuItem").hide();
                }
                else {
                    $("#inviteMenuItem").show();
                }
            }
            else {
                $("#teamLabel").text("No team");
                $("#rankLabel").text("No rank");
                $("#inviteMenuItem").hide();
            }

            var battleCharacterInfo = action.battle_character_info.split(":");

            $("#battleStrengthLabel").text(battleCharacterInfo[2]);
            $("#battleDexterityLabel").text(battleCharacterInfo[3]);
            $("#battleIntellectLabel").text(battleCharacterInfo[4]);
            $("#battleWisdomLabel").text(battleCharacterInfo[5]);
            $("#battleConstitutionLabel").text(battleCharacterInfo[6]);
            $("#battleAttackLabel").text(battleCharacterInfo[7]);
            $("#battleDefenceLabel").text(battleCharacterInfo[8]);
            $("#battleMagicAttackLabel").text(battleCharacterInfo[9]);
            $("#battleMagicDefenceLabel").text(battleCharacterInfo[10]);
            $("#battleArmorLabel").text(battleCharacterInfo[11]);
            $("#battleGoldLabel").text(battleCharacterInfo[12]);

            // set health and mana bars
            $("#HPLabel").text(battleCharacterInfo[0] + "/" + characterInfo[4]);
            $("#whiteHPLabel").text(battleCharacterInfo[0] + "/" + characterInfo[4]);
            $("#MPLabel").text(battleCharacterInfo[1] + "/" + characterInfo[5]);
            $("#whiteMPLabel").text(battleCharacterInfo[1] + "/" + characterInfo[5]);
            $("#healthBar").removeClass("bar-health");
            $("#healthBar").removeClass("bar-health-low");
            $("#healthBar").removeClass("bar-health-very-low");
            healthPercent = battleCharacterInfo[0]/characterInfo[4] * 100;
            $("#healthBar").width(healthPercent + "%");
            if (healthPercent < 20) {
                $("#healthBar").addClass("bar-health-very-low");
            }
            else if (healthPercent < 40) {
                $("#healthBar").addClass("bar-health-low");
            }
            else {
                $("#healthBar").addClass("bar-health");
            }
            $("#manaBar").width(battleCharacterInfo[1]/characterInfo[5] * 100 + "%");
            $("#experienceLabel").text(characterInfo[16] + "/" + characterInfo[17]);
            $("#whiteExperienceLabel").text(characterInfo[16] + "/" + characterInfo[17]);
            $("#experienceBar").width(characterInfo[16]/characterInfo[17] * 100 + "%");
            $("#whiteExperienceLabel").width($("#experienceBar").parent().width());
            $("#whiteHPLabel").width($("#healthBar").parent().width());
            $("#whiteMPLabel").width($("#manaBar").parent().width());
        }
        // character stuff update
        else if (action.type == 201) {
            $("#bagStuffTable td").empty();
            $("#characterStuffTable td").empty();
            if (action.right_hand) {
                showWornItem($("#right_handCell"), action.right_hand);
            }
            if (action.left_hand) {
                showWornItem($("#left_handCell"), action.left_hand);
            }
            if (action.head) {
                showWornItem($("#headCell"), action.head);
            }
            if (action.body) {
                showWornItem($("#bodyCell"), action.body);
            }
            if (action.hands) {
                showWornItem($("#handsCell"), action.hands);
            }
            if (action.legs) {
                showWornItem($("#legsCell"), action.legs);
            }
            if (action.feet) {
                showWornItem($("#feetCell"), action.feet);
            }
            if (action.cloak) {
                showWornItem($("#cloakCell"), action.cloak);
            }
            if (action.bag) {
                showBagItems(action.bag);
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
            removeTeamChat();
        }
        // show team info div
        else if (action.type == 204) {
            $("#teamDivContainer").empty();
            $("#teamDivContainer").append(action.team_div);
            initialize_team_info();
            addTeamChat(action.team_name);
        }
        // add invitation
        else if (action.type == 205) {
            $("#divInvitationContent").empty();
            $("#divInvitationContent").append(action.invitation_div);
            initialize_team_invitation(action.user_name, action.team_name);
        }
        // text message
        else if (action.type == 300){
            message = action;
            if(message.type == "location") {
                addTextTo("#locationTab", format_message(message))
            }
            // not location, maybe team?
            else if (message.type == "team") {
                addTextTo("#teamTab", format_message(message))
            }
            // not location, not team - private
            else if (message.type == "private") {
                // message from yourself
                if (message.from == $("#nameLabel").text()) {
                    addTextTo("#" + message.to + "Tab", format_private_message(message, false))
                }
                // message from another user
                else {
                    if ($("#" + message.from + "Tab").length == 0) {
                        $.postJSON('/action', {"action" : "open_chat", "user_name" : message.from, "message" : format_private_message(message, true)}, function(response) {
                        });
                    }
                    else {
                        addTextTo("#" + message.from + "Tab", format_private_message(message, true))
                    }
                }
            }
        }

        pollUpdater.errorSleepTime = 500;
        window.setTimeout(pollUpdater.poll, 0);
        $("#serverStatus").html("Connected");
    },

    onError: function() {
        $("#serverStatus").html("Disconnected");
        pollUpdater.errorSleepTime *= 2;
        window.setTimeout(pollUpdater.poll, pollUpdater.errorSleepTime);
    }
};
