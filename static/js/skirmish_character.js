/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 15:05
 */

var initialize_character = function() {
    $("#characterStuffTable span").live({
        contextmenu : function(e){
            $.postJSON('/action', {"action" : "take_off", "item_id" : $(this).attr("value")}, function() {
            });
            return false;
        }
    });

    $("#bagStuffTable span").live({
        contextmenu : function(e){
            $.postJSON('/action', {"action" : "put_on", "item_id" : $(this).attr("value")}, function(response) {
                if (response == "false") {
                }
            });
            return false;
        }
    });
};

var showWornItem = function(itemCell, item) {
    if (item) {
        itemCell.append(item);
        $(itemCell).find("span").popover({
            delay: { show: 1000, hide: 100 },
            placement : "top"
        });
    }
};

var showBagItems = function(items) {
    for (i = 0; i < items.length; i++) {
        itemCell = $("#bagStuffTable td:empty:first");
        itemCell.append(items[i]);
        $(itemCell).find("span").popover({
            delay: { show: 1000, hide: 100 },
            placement : "top",
            content : "AAA"
        });
    }
};

var learnSpellFunc = function() {
    $.postJSON('/action', {"action" : "learn_spell", "spell_id" : $(this).attr("spell_id")}, function(response) {
    });
};
