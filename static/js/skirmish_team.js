/**
 * Author: Pavel Padinker
 * Date: 13.05.12
 * Time: 14:14
 */

var initialize_create_team = function () {
    $("#createTeamButton").click(createTeamFunc);
};

var initialize_team_info = function () {
    $("#leaveTeamButton").click(leaveTeamFunc);
    $("#goldTaxSelect").change(changeGoldTaxFunc);
    $("#goldSharingSelect").change(changeGoldSharingFunc);
    $("#experienceSharingSelect").change(changeExperienceSharingFunc);

    $("#divTeam button[class=promoteButton]").click(promoteFunc);
    $("#divTeam button[class=demoteButton]").click(demoteFunc);
    $("#divTeam button[class=removeButton]").click(removeFunc);
};

var initialize_team_invitation = function(user_name, team_name) {
    $("#divInvitation").data("invitation", {"user_name" : user_name, "team_name" : team_name});
    $("#confirmButton").click(confirmFunc);
    $("#declineButton").click(declineFunc);
};

var changeGoldTaxFunc = function() {
    $.postJSON('/action', {"action" : "change_gold_tax", "strategy" : $("option:selected", this).val()}, function() {
    });
};

var changeGoldSharingFunc = function() {
    $.postJSON('/action', {"action" : "change_gold_sharing", "strategy" : $("option:selected", this).val()}, function() {
    });
};

var changeExperienceSharingFunc = function() {
    $.postJSON('/action', {"action" : "change_experience_sharing", "strategy" : $("option:selected", this).val()}, function() {
    });
};

var createTeamFunc = function() {
    $.postJSON('/action', {"action" : "create_team", "team_name" : $("#teamName").val()}, function(response) {
        var res = $.parseJSON(response);
        if(res.error) {
            $("#errorLabel").html(res.msg)
        }
    });
};

var promoteFunc = function() {
    $.postJSON('/action', {"action" : "promote_team", "user_name" : $(this).attr("user_name")}, function() {
    });
};

var demoteFunc = function() {
    $.postJSON('/action', {"action" : "demote_team", "user_name" : $(this).attr("user_name")}, function() {
    });
};

var removeFunc = function() {
    $.postJSON('/action', {"action" : "remove_team", "user_name" : $(this).attr("user_name")}, function() {
    });
};

var confirmFunc = function() {
    $.postJSON('/action', {"action" : "confirm_team", "user_name" : $("#divInvitation").data("invitation").user_name, "team_name" : $("#divInvitation").data("invitation").team_name}, function(response) {
        hideInvitation();
    });
};

var declineFunc = function() {
    $.postJSON('/action', {"action" : "decline_team", "user_name" : $("#divInvitation").data("invitation").user_name, "team_name" : $("#divInvitation").data("invitation").team_name}, function(response) {
        hideInvitation();
    });
};

var hideInvitation = function() {
    $("#divInvitationContent").empty();
};

var leaveTeamFunc = function() {
    $.postJSON('/action', {"action" : "leave_team"}, function(response) {
    });
};
