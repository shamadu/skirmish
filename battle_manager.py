from battle_bot import BattleBot

__author__ = 'Pavel Padinker'

class BattleManager():
    def __init__(self, actions_manager):
        self.actions_manager = actions_manager
        self.battle_bots = {
            "En" : BattleBot(actions_manager, "En"),
            "Ru" : BattleBot(actions_manager, "Ru")
        }
        for battle_bot in self.battle_bots.values():
            battle_bot.start()

    @property
    def online_users(self):
        return self.actions_manager.online_users

    def remove_from_skirmish(self, user_name):
        self.battle_bots[self.online_users[user_name].location].remove_from_skirmish(user_name)

    def subscribe(self, user_name, callback):
        self.online_users[user_name].set_skirmish_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_skirmish_callback(None)

    def user_join(self, user_name):
        self.battle_bots[self.online_users[user_name].location].user_join(user_name)

    def user_leave(self, user_name):
        self.battle_bots[self.online_users[user_name].location].user_leave(user_name)

    def user_turn(self, user_name, turn_info):
        self.battle_bots[self.online_users[user_name].location].user_turn(user_name, turn_info)

    def user_turn_cancel(self, user_name):
        self.battle_bots[self.online_users[user_name].location].user_turn_cancel(user_name)

    def user_enter(self, user_name):
        self.battle_bots[self.online_users[user_name].location].user_enter(user_name)
