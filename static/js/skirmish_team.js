/**
 * Author: Pavel Padinker
 * Date: 13.05.12
 * Time: 14:14
 */

var initialize_team = function () {
    $("#createTeamButton").click(createTeamFunc);
};

var createTeamFunc = function() {
    $.postJSON('/team/create', {"team_name" : $("#teamName").val()}, function() {

    });
};