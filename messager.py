__author__ = 'Pavel'

class Messager():
    def __init__(self):
        self.callbacks = dict()
        self.cache = dict()
        pass

    def subscribe(self, name, callback):
        if not name in self.callbacks:
            self.callbacks[name] = callback
            for message in self.cache:
                callback(message)

    def unsubscribe(self, name):
        if name in self.callbacks:
            self.callbacks.pop(name)

    def new_message(self,message):
        to_whom = message["to"]
        if to_whom == "all":
            for callback in self.callbacks.values():
                callback(message)
        elif to_whom in self.callbacks:
            self.callbacks[to_whom](message)
        elif to_whom in self.cache:
            self.cache[to_whom].append(message)
        else:
            self.cache[to_whom] = list()

        self.callbacks.clear()
