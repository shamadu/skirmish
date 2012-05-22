/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 15:05
 */

var initialize_shop = function() {
    max_width1 = 0;
    li_first_level = new Array();
    $("#shopMenu >ul>li").each(function(){
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
            $(this).click(getItemFunc);
        });
    }
};

var getItemFunc = function() {
    $.postJSON('/shop', {"action" : "get_item", "item_id" : $(">a", this).attr('item_id')}, function(response) {
        $("#itemDescriptions").append(response);
        $("#itemDescriptions >div:last").width($("#itemDescriptions >div:last >table").width());
        $("#itemDescriptions >div:last >button.close").click(closeDescription);
    });
};

var closeDescription = function() {
    $(this).parent().remove();
}