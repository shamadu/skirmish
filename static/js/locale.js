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
messages[0] = {{ '"%s"' % _("Registration has been started") }};
messages[1] = {{ '"%s"' % _("Registration has been ended") }};
messages[2] = {{ '"%s"' % _("Round {0} has been started") }};
messages[3] = {{ '"%s"' % _("Round {0} has been ended") }};
messages[4] = {{ '"%s"' % _("Game has been ended") }};
messages[5] = {{ '"%s"' % _("Game can't be started, not enough players") }};
messages[6] = {{ '"%s"' % _("Incorrect percentage of the action. Incorrect values were changed to 0") }};
messages[7] = {{ '"%s"' % _("Nothing to do. Please do your turn") }};