/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 15:05
 */

var initialize_shop = function() {
    initialize_dropDown($("#shopMenu"), getShopItemFunc)
};

var initialize_DB = function() {
    initialize_dropDown($("#dbMenu"), getDBItemFunc)
};

var initialize_dropDown = function(dropDown, clickHandler) {
    max_width1 = 0;
    li_first_level = new Array();
    $(dropDown).find(">ul>li").each(function(){
        width = $(">a", this).width();
        if (width > max_width1) {
            max_width1 = width;
        }

        li_first_level.push(this);
    });
    max_width1 += 20;

    for (i = 0; i < li_first_level.length; i++) {
        $(li_first_level[i]).width(max_width1);
    }

    for (i = 0; i < li_first_level.length; i++) {
        $(">ul", li_first_level[i]).css("left", max_width1 + 20);
        max_width2 = 0;
        $(">ul>li", li_first_level[i]).each(function(){
            width = $(">a", this).width();
            if (width > max_width2) {
                max_width2 = width;
            }
        });
        max_width2 += 10;

        $(">ul>li", li_first_level[i]).each(function(){
            $(this).width(max_width2);
            $(this).click(clickHandler);
        });
    }
}

var getShopItemFunc = function() {
    if ($("#shopItemDescriptions div[item_id=" + $(">a", this).attr('item_id') + "]").length == 0) {
        $.postJSON('/shop', {"action" : "get_item", "item_id" : $(">a", this).attr('item_id')}, function(response) {
            $("#shopItemDescriptions").append(response);
            $("#shopItemDescriptions >div:last").width($("#shopItemDescriptions >div:last >table").width());
            $("#shopItemDescriptions >div:last >button.close").click(closeDescription);
            $("#shopItemDescriptions >div:last button.buyButton").click(buyItem);
        });
    }
};

var getDBItemFunc = function() {
    if ($("#dbItemDescriptions div[item_id=" + $(">a", this).attr('item_id') + "]").length == 0) {
        $.postJSON('/db', {"action" : "get_item", "item_id" : $(">a", this).attr('item_id')}, function(response) {
            $("#dbItemDescriptions").append(response);
            $("#dbItemDescriptions >div:last").width($("#dbItemDescriptions >div:last >table").width());
            $("#dbItemDescriptions >div:last >button.close").click(closeDescription);
        });
    }
};

var closeDescription = function() {
    $(this).parent().remove();
};

var buyItem = function() {
    $.postJSON('/shop', {"action" : "buy_item", "item_id" : $(this).attr('item_id')}, function(response) {
    });
    $(this).closest("div").remove();
};