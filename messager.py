__author__ = 'Pavel'

class Messager():
    def __init__(self):
        self.callbacks = dict()
        self.cache = dict()
        pass

    def run(self):
        while 1:
            pass

    def subscribe(self, name, callback):
        if not self.callbacks[name]:
            self.callbacks[name] = callback
            for message in self.cache[name]:
                callback(message)

    def unsubscribe(self, name):
        if self.callbacks[name]:
            self.callbacks.pop(name)

    def new_message(self,message):
        to_whom = message["to"]
        if to_whom == "all":
            for callback in self.callbacks.values():
                callback(message)
        elif self.callbacks[to_whom]:
            self.callbacks[to_whom](message)
        elif self.cache[to_whom]:
            self.cache[to_whom].append(message)
        else:
            self.cache[to_whom] = list()
        pass