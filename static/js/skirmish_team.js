/**
 * Author: Pavel Padinker
 * Date: 13.05.12
 * Time: 14:14
 */

var initialize_create_team = function () {
    $("#createTeamButton").click(createTeamFunc);
};

var initialize_team_info = function () {
    $("#divOnlineUsers label").each(function(){
        $("#inviteUserSelect").append("<option value=\"" + $(this).html() + "\">" + $(this).html() + "</option>")
    });
    $("#inviteUserButton").click(inviteUserFunc);
    $("#leaveTeamButton").click(leaveTeamFunc);

    $("#divTeam button[class=promoteButton]").click(promoteFunc);
    $("#divTeam button[class=demoteButton]").click(demoteFunc);
    $("#divTeam button[class=removeButton]").click(removeFunc);
};

var initialize_team_invitation = function(user_name, team_name) {
    $("#divInvitation").data("invitation", {"user_name" : user_name, "team_name" : team_name});
    $("#confirmButton").click(confirmFunc);
    $("#declineButton").click(declineFunc);
};

var createTeamFunc = function() {
    $.postJSON('/team', {"action" : "create", "team_name" : $("#teamName").val()}, function(response) {
        var res = $.parseJSON(response);
        if(res.error) {
            $("#errorLabel").html(res.msg)
        }
    });
};

var promoteFunc = function() {
    $.postJSON('/team', {"action" : "promote", "user_name" : $(this).attr("user_name")}, function() {
    });
};

var demoteFunc = function() {
    $.postJSON('/team', {"action" : "demote", "user_name" : $(this).attr("user_name")}, function() {
    });
};

var removeFunc = function() {
    $.postJSON('/team', {"action" : "remove", "user_name" : $(this).attr("user_name")}, function() {
    });
};

var inviteUserFunc = function() {
    $.postJSON('/team', {"action" : "invite", "user_name" : $("#inviteUserSelect option:selected").html()}, function(response) {
        var res = $.parseJSON(response);
        window.alert(res.msg);
    });
};

var confirmFunc = function() {
    $.postJSON('/team', {"action" : "confirm", "user_name" : $("#divInvitation").data("invitation").user_name, "team_name" : $("#divInvitation").data("invitation").team_name}, function(response) {
        hideInvitation();
    });
};

var declineFunc = function() {
    $.postJSON('/team', {"action" : "decline", "user_name" : $("#divInvitation").data("invitation").user_name, "team_name" : $("#divInvitation").data("invitation").team_name}, function(response) {
        hideInvitation();
    });
};

var hideInvitation = function() {
    $("#divInvitationContent").empty();
};

var leaveTeamFunc = function() {
    $.postJSON('/team', {"action" : "leave"}, function(response) {
    });
};
