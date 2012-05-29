/**
 * Author: Pavel Padinker
 * Date: 19.04.12
 * Time: 12:38
 */

String.prototype.format = String.prototype.f = function() {
    var s = this,
            i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

var messages = new Object();
messages[0] = {{ '"%s"' % _("Incorrect percentage of the action. Incorrect values were changed to 0") }};
messages[1] = {{ '"%s"' % _("Nothing to do. Please do your turn") }};