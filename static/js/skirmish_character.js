/**
 * Author: Pavel Padinker
 * Date: 12.05.12
 * Time: 15:05
 */

var initialize_character = function () {
    characterInfoUpdater.poll();
};

var characterInfoUpdater = {
    errorSleepTime: 500,

    poll: function() {
        $.postJSON('/info/poll', {}, characterInfoUpdater.onSuccess, characterInfoUpdater.onError);
    },

    onSuccess: function(response) {
        var action = $.parseJSON(response);
        // character info update
        if (action.type == 0) {
            var characterInfo = action.character_info.split(":");
            $("#nameLabel").text(characterInfo[0]);
            $("#classLabel").text(characterInfo[1]);
            $("#levelLabel").text(characterInfo[2]);
            $("#HPLabel").text(characterInfo[3]);
            $("#MPLabel").text(characterInfo[4]);
            $("#strengthLabel").text(characterInfo[5]);
            $("#dexterityLabel").text(characterInfo[6]);
            $("#intellectLabel").text(characterInfo[7]);
            $("#wisdomLabel").text(characterInfo[8]);

            $("#nameLabel_battle").text(characterInfo[0]);
            $("#classLabel_battle").text(characterInfo[1]);
            $("#levelLabel_battle").text(characterInfo[2]);
            $("#HPLabel_battle").text(characterInfo[3]);
            $("#MPLabel_battle").text(characterInfo[4]);
        }

        characterInfoUpdater.errorSleepTime = 500;
        window.setTimeout(characterInfoUpdater.poll, 0);
    },

    onError: function() {
        characterInfoUpdater.errorSleepTime *= 2;
        window.setTimeout(characterInfoUpdater.poll, characterInfoUpdater.errorSleepTime);
    }
};
