import random
import string
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.database
import os
from bot import Bot
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
            (r'/bot/users/poll', PollUsersHandler,),
            (r'/bot/users/onstart', UsersHandler,),
            (r'/bot/message/poll', PollMessageHandler,),
            (r'/bot/message/new', NewMessageHandler,),
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
        self.bot = Bot()
        self.bot.start()

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
    def bot(self):
        return self.application.bot

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
            self.bot.user_online(self.current_user)

class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if not self.current_user:
            self.render("login.html")
        else:
            self.redirect("/")

    def post(self, *args, **kwargs):
        login_response = {
            'error': False,
            'msg': ''
        }

        login = self.get_argument("login")
        password = self.get_argument("password")

        # try to find user with this login in db:
        user = self.db.get("select * from users where login = %s", login)
        if not user:
            # no such user - insert the new one
            self.db.execute("insert into users (login, password) values (%s, %s)", login, password)
            self.set_secure_cookie("login", login)
        elif user["password"] == password:
            self.set_secure_cookie("login", login)
        else:
            login_response["error"] = True
            login_response["msg"] = "Error : can't log in, wrong login or password"

        if not login_response["error"]:
            login_response["msg"] = self.get_current_user()

        self.write(login_response)

class LogoutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.bot.user_offline(self.current_user)
        self.clear_cookie("login")

class CreateCharacterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        character = self.characters_manager.get(self.current_user)
        if not character:
        # no such user - redirect to creation
            self.render("create.html", name=self.current_user)
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
        if self.get_argument("action") == 'classes_list':
            self.write(self.characters_manager.get_classes())
        elif self.get_argument("action") == 'character_info':
            character_info = self.characters_manager.get_info(self.current_user)
            character_info['status'] = self.bot.get_user_status(self.current_user)
            self.write(character_info)

class BattleBotHandler(BaseHandler):
    def post(self, *args, **kwargs):
        if self.get_argument("action") == 'join':
            self.bot.user_join(self.current_user)
        elif self.get_argument("action") == 'leave':
            self.bot.user_leave(self.current_user)

class PollUsersHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.bot.subscribe(self.current_user, self.on_users_changed)

    def on_users_changed(self, users):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(users)

    def on_connection_close(self):
        self.bot.unsubscribe(self.current_user)

class UsersHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        self.write(self.bot.get_users())

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