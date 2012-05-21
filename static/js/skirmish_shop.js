/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 15:05
 */

var initialize_shop = function() {
    max_width1 = 0;
    $("#shopMenu ul>li").each(function(){
        width1 = $(">a", this).width();
        if (width1 > max_width1) {
            max_width1 = width1;
        }

        max_width2 = 0;
        $("ul>li", this).each(function(){
            width2 = $(">a", this).width();
            if (width2 > max_width2) {
                max_width2 = width2;
            }
        });
        max_width2 += 10;

        $("ul>li", this).each(function(){
            $(this).width(max_width2);
        });
    });
    max_width1 += 10;

    $("#shopMenu ul>li").each(function(){
        $(this).width(max_width1);
    });
}