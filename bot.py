from threading import Thread

__author__ = 'Pavel'

class Bot(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.skirmish_users = list()
        self.online_users = list()
        self.callbacks = dict()

    def run(self):
        while 1:
            pass

    def user_join(self, name):
        if not name in self.skirmish_users:
            self.skirmish_users.append(name)

    def user_leave(self, name):
        if name in self.skirmish_users:
            self.skirmish_users.remove(name)

    def user_online(self, name):
        if not name in self.online_users:
            self.online_users.append(name)
            for online_callback in self.callbacks.values():
                online_callback(self.get_users())

    def user_offline(self, name):
        if name in self.online_users:
            self.online_users.remove(name)
            self.unsubscribe(name)
            for online_callback in self.callbacks.values():
                online_callback(self.get_users())

    def subscribe(self, name, callback):
        if name in self.online_users:
            self.callbacks[name] = callback

    def unsubscribe(self, name):
        if name in self.callbacks:
            self.callbacks.pop(name)

    def get_user_status(self, name):
        if name in self.skirmish_users:
            return 'battle'
        else:
            return 'rest'

    def get_users(self):
         return {"online" : ', '.join(self.online_users), "skirmish" : ', '.join(self.skirmish_users)}