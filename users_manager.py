from threading import Thread
import time
import smarty

__author__ = 'Pavel Padinker'

class UsersManager(Thread):
    def __init__(self, db_manager, actions_manager):
        Thread.__init__(self)
        self.online_users = actions_manager.online_users
        self.db_manager = db_manager
        self.actions_manager = actions_manager

    def run(self):
        while 1:
            for user_name in self.online_users.keys():
                if not self.online_users[user_name].user_callback and not self.online_users[user_name].skirmish_callback and not self.online_users[user_name].character_callback:
                    if not self.online_users[user_name].counter:
                        self.user_logout(user_name)
                    else:
                        self.online_users[user_name].counter -= 1

            time.sleep(1)
            pass

    def user_login(self, login, password):
        login_response = {
            'error': False,
            'msg': ''
        }

        # try to find user with this login in db:
        user = self.db_manager.get_user(login)
        if not user:
            # no such user - add new one
            self.db_manager.add_user(login, password)
        elif user["password"] != password:
            login_response["error"] = True
            login_response["msg"] = smarty.error_messages[2]

        if not login_response["error"]:
            login_response["msg"] = login

        return login_response

    def user_logout(self, user_name):
        if user_name in self.online_users.keys():
            self.actions_manager.remove_online_user(user_name)

    def subscribe(self, user_name, callback):
        self.online_users[user_name].set_user_callback(callback)

    def unsubscribe(self, user_name):
        if user_name in self.online_users:
            self.online_users[user_name].set_user_callback(None)

    def user_enter(self, user_name):
        self.actions_manager.user_enter_users_manager(user_name)

    def change_location(self, user_name, location):
        self.actions_manager.change_location(user_name, location)
        self.online_users[user_name].location = location
        self.actions_manager.user_enter(user_name)
