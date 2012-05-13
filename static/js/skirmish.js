/**
 * Author: Pavel Padinker
 * Date: 17.04.12
 * Time: 11:00
 */

var initialize = function () {
    initialize_battle();
    initialize_character();

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