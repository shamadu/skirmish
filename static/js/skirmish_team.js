/**
 * Author: Pavel Padinker
 * Date: 13.05.12
 * Time: 14:14
 */

var initialize_create_team = function () {
    $("#createTeamButton").click(createTeamFunc);
};

var initialize_team_info = function () {
    $("#divTeam button[class=promoteButton]").click(promoteFunc);
    $("#divTeam button[class=demoteButton]").click(demoteFunc);
    $("#divTeam button[class=removeButton]").click(removeFunc);
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
    $.postJSON('/team', {"action" : "promote", "user_name" : $(this).attr("user_name")}, function(response) {
    });
};

var demoteFunc = function() {
    $.postJSON('/team', {"action" : "demote", "user_name" : $(this).attr("user_name")}, function(response) {
    });
};

var removeFunc = function() {
    $.postJSON('/team', {"action" : "remove", "user_name" : $(this).attr("user_name")}, function(response) {
    });
};