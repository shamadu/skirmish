/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 15:05
 */

var initialize_character = function() {
    $("#bagStuffTable span").live({
        contextmenu : function(e){
            $.postJSON('/action', {"action" : "put_on", "thing_id" : $(this).attr("value")}, function(response) {
                if (response == "false") {
                }
            });
            return false;
        }
    });
};

var showWornItem = function(itemCell, item) {
    if (item) {
        // thing[0]:thing[1]
        // 0 is id, 1 is name
        thing = item.split(":");
        itemCell.append("<span value=\"" + thing[0] + "\" class=\"span-item-icon\">" + thing[1] + "</span>");
    }
};

var showBagItems = function(items) {
    arrItems = items.split(",");
    for (i = 0; i < arrItems.length; i++) {
        thing = arrItems[i].split(":");
        $("#bagStuffTable td:empty:first").append("<span value=\"" + thing[0] + "\" class=\"span-item-icon\">" + thing[1] + "</span>");
    }
};

var learnSpellFunc = function() {
    $.postJSON('/action', {"action" : "learn_spell", "spell_id" : $(this).attr("spell_id")}, function(response) {
    });
};
