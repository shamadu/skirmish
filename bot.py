from threading import Thread

__author__ = 'Pavel'

class Bot(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.skirmish_users = list()

    def run(self):
        while 1:
            pass

    def add_user(self, name):
        if not name in self.skirmish_users:
            self.skirmish_users.append(name)

    def remove_user(self, name):
        if name in self.skirmish_users:
            self.skirmish_users.remove(name)

    def get_user_status(self, name):
        if name in self.skirmish_users:
            return 'battle'
        else:
            return 'rest'
