/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 15:05
 */

var initialize_character = function() {
    $("#characterStuffTable select").each(function(){
        $(this).change(putOnFunc);
    })
};

var putOnFunc = function() {
    this_select = this;
    $.postJSON('/action', {"action" : "put_on", "thing_id" : $("option:selected", this).val()}, function(response) {
        if (response == "false") {
            $("option:first", this_select).attr("selected", "selected");
        }
    });
};

var addThings = function(things, select) {
    select.empty();
    arrThings = things.split(",");
    for (i = 0; i < arrThings.length; i++) {
        thing = arrThings[i].split(":"); // 0 is id, 1 is name
        select.append("<option value=\"" + thing[0] + "\">" + thing[1] + "</option>");
    }
};

var learnSpellFunc = function() {
    $.postJSON('/action', {"action" : "learn_spell", "spell_id" : $(this).attr("spell_id")}, function(response) {
    });
}
