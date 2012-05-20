/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 15:05
 */

var initialize_character = function() {
    $("#characterStuffTable select").each(function(){
        $(this).change(putOnFunc);
    })
}

var putOnFunc = function() {
    $.postJSON('/character', {"action" : "put_on", "thing_id" : $("option:selected", this).val()}, function() {
    });
}