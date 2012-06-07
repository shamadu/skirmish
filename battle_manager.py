from battle_bot import BattleBot

__author__ = 'Pavel Padinker'

class BattleManager():
    def __init__(self, users_holder, db_manager, characters_manager):
        self.users_holder = users_holder
        self.battle_bots = {
            "En" : BattleBot(users_holder, db_manager, characters_manager, "En"),
            "Ru" : BattleBot(users_holder, db_manager, characters_manager, "Ru")
        }
        for battle_bot in self.battle_bots.values():
            battle_bot.start()

    @property
    def online_users(self):
        return self.users_holder.online_users

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

