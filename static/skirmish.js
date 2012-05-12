/**
 * Author: Pavel Padinker
 * Date: 17.04.12
 * Time: 11:00
 */

var initialize = function () {
    initialize_battle();

    width = $("#sideBar").width();
    $("#contentDiv").css('left', width + 5 + 'px');

    showBattle();
    $("#battleAnchor").click(showBattle);
    $("#characterAnchor").click(showCharacter);
    $("#teamAnchor").click(showTeam);
};

var showBattle = function() {
    $("#battleDiv").show();
    $("#battleAnchor").parent().attr("class", "active");
    $("#characterDiv").hide();
    $("#characterAnchor").parent().removeAttr("class");
    $("#teamDiv").hide();
    $("#teamAnchor").parent().removeAttr("class");
};

var showCharacter = function() {
    $("#characterDiv").show();
    $("#characterAnchor").parent().attr("class", "active");
    $("#battleDiv").hide();
    $("#battleAnchor").parent().removeAttr("class");
    $("#teamDiv").hide();
    $("#teamAnchor").parent().removeAttr("class");
};

var showTeam = function() {
    $("#teamDiv").show();
    $("#teamAnchor").parent().attr("class", "active");
    $("#battleDiv").hide();
    $("#battleAnchor").parent().removeAttr("class");
    $("#characterDiv").hide();
    $("#characterAnchor").parent().removeAttr("class");
};