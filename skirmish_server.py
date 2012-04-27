import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.database
import os
from battle_bot import BattleBot
from users_manager import UsersManager
from characters_manager import CharactersManager
from messager import Messager

__author__ = 'PavelP'

class SkirmishApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler,),
            (r'/login', LoginHandler,),
            (r'/logout', LogoutHandler,),
            (r'/create', CreateCharacterHandler,),
            (r'/drop', DropCharacterHandler,),
            (r'/info', InfoCharacterHandler,),
            (r'/bot/battle', BattleBotHandler,),
            (r'/bot/poll', PollBotHandler,),
            (r'/users/poll', PollUsersHandler,),
            (r'/message/poll', PollMessageHandler,),
            (r'/message/new', NewMessageHandler,),
        ]
        settings = {
            "cookie_secret" : "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "login_url": "/login",
            "xsrf_cookies": True,
            "static_path" : os.path.join(os.path.dirname(__file__), "static"),
            }

        tornado.web.Application.__init__(self, handlers, **settings)

        # have one global connection to the application db across all handlers
        self.db = tornado.database.Connection(
            host="127.0.0.1:3306", database="users",
            user="root", password="passw0rd")

        # uncomment in case db should be created - first start
        self.db.execute("create table if not exists users (id integer(11) primary key not null auto_increment unique, "
                        "login text, password text)")

        self.characters_manager = CharactersManager(self.db)
        self.users_manager = UsersManager(self.db)
        self.users_manager.start()

        self.battle_bot = BattleBot()
        self.battle_bot.start()

        self.messager = Messager()

        self.online_users = dict()

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def characters_manager(self):
        return self.application.characters_manager

    @property
    def users_manager(self):
        return self.application.users_manager

    @property
    def battle_bot(self):
        return self.application.battle_bot

    @property
    def messager(self):
        return self.application.messager

    def get_current_user(self):
        return self.get_secure_cookie("login")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        character = self.characters_manager.get(self.current_user)
        if not character:
        # no such user - redirect to creation
            self.redirect("/create")
        else:
            self.render("skirmish.html", login=self.current_user)
            self.users_manager.reset_user(self.current_user)
            self.battle_bot.send_skirmish_users_to(self.current_user)

class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if not self.current_user:
            self.render("login.html")
        else:
            self.redirect("/")

    def post(self, *args, **kwargs):
        login = self.get_argument("login")
        login_response = self.users_manager.user_login(login, self.get_argument("password"))

        if not login_response["error"]:
            self.set_secure_cookie("login", login)

        self.write(login_response)

class LogoutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.users_manager.user_logout(self.current_user)
        self.clear_cookie("login")

class CreateCharacterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        character = self.characters_manager.get(self.current_user)
        if not character:
        # no such user - redirect to creation
            self.render("create.html", name=self.current_user, classes=self.characters_manager.get_classes())
        else:
            self.redirect("/")

    def post(self, *args, **kwargs):
        classID = self.get_argument("classID")
        # insert the new character
        self.characters_manager.create(self.current_user, classID)

class DropCharacterHandler(BaseHandler):
    def get(self, *args, **kwargs):
        # remove the character from DB
        self.characters_manager.remove(self.current_user)

class InfoCharacterHandler(BaseHandler):
    def post(self, *args, **kwargs):
        character_info = self.characters_manager.get_info(self.current_user)
        character_info['status'] = self.battle_bot.get_user_status(self.current_user)
        self.write(character_info)

class BattleBotHandler(BaseHandler):
    def post(self, *args, **kwargs):
        if self.get_argument("action") == 'join':
            self.battle_bot.user_join(self.current_user)
        elif self.get_argument("action") == 'leave':
            self.battle_bot.user_leave(self.current_user)

class PollBotHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.battle_bot.subscribe(self.current_user, self.on_users_changed)

    def on_users_changed(self, users):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(users)

    def on_connection_close(self):
        self.battle_bot.unsubscribe(self.current_user)

class PollUsersHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.users_manager.subscribe(self.current_user, self.on_users_changed)

    def on_users_changed(self, users):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(users)

    def on_connection_close(self):
        self.users_manager.unsubscribe(self.current_user)

class PollMessageHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.messager.subscribe(self.current_user, self.on_new_message)

    def on_new_message(self, message):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(message)

    def on_connection_close(self):
        self.messager.unsubscribe(self.current_user)

class NewMessageHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        message = {
            "from": self.current_user,
            "to": self.get_argument("to"),
            "body": self.get_argument("body"),
            }
        self.messager.new_message(message)

def main():
    http_server = tornado.httpserver.HTTPServer(SkirmishApplication())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()