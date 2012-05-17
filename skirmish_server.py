from tornado import web
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.database
import tornado.locale
from battle_bot import BattleBot
from db_manager import DBManager
from online_users_holder import OnlineUsersHolder
from smarty import get_classes
import smarty
from users_manager import UsersManager
from characters_manager import CharactersManager
from messager import Messager

__author__ = 'Pavel Padinker'

class SkirmishApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler,),
            (r'/static/js/locale.js', StaticJSHandler,),
            (r"/static/(.*)", web.StaticFileHandler, {"path": "static"}),
            (r"/(favicon\.ico)", web.StaticFileHandler, {"path": "static"}),
            (r"/(robots\.txt)", web.StaticFileHandler, {"path": ""}),
            (r'/login', LoginHandler,),
            (r'/logout', LogoutHandler,),
            (r'/create', CreateCharacterHandler,),
            (r'/drop', DropCharacterHandler,),
            (r'/bot/battle', BattleBotHandler,),
            (r'/bot/poll', PollBotHandler,),
            (r'/users/poll', PollUsersHandler,),
            (r'/message/poll', PollMessageHandler,),
            (r'/info/poll', PollCharacterInfoHandler,),
            (r'/message/new', NewMessageHandler,),
            (r'/team', TeamHandler,),
        ]
        settings = {
            "cookie_secret" : "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "login_url" : "/login",
            "xsrf_cookies" : True,
            "template_path" : "templates"
            }

        tornado.web.Application.__init__(self, handlers, **settings)

        # have one global connection to the application db across all handlers
        self.db = tornado.database.Connection(
            host="127.0.0.1:3306", database="users",
            user="root", password="passw0rd")

        self.db_manager = DBManager(self.db)
        self.online_users_holder = OnlineUsersHolder(self.db_manager)

        self.users_manager = UsersManager(self.db_manager, self.online_users_holder)
        self.users_manager.start()

        self.online_users_holder.users_manager = self.users_manager

        self.battle_bot = BattleBot(self.db_manager, self.online_users_holder)
        self.battle_bot.start()

        self.characters_manager = CharactersManager(self.db_manager, self.online_users_holder)
        self.messager = Messager()

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def characters_manager(self):
        return self.application.characters_manager

    @property
    def db_manager(self):
        return self.application.db_manager

    @property
    def online_users_holder(self):
        return self.application.online_users_holder

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

    def get_user_locale(self):
        return tornado.locale.get(self.get_cookie("locale"))

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        character = self.db_manager.get_character(self.current_user)
        if not character:
        # no such user - redirect to creation
            self.redirect("/create")
        else:
            # this sequence is important!
            self.characters_manager.user_enter(self.current_user, self.locale)
            self.online_users_holder.user_enter(self.current_user, self.locale)
            self.battle_bot.user_enter(self.current_user, self.locale)

            self.render("skirmish.html",
                login=self.current_user,
                substance=smarty.get_substance_name(character.classID, self.locale))

class StaticJSHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "text/javascript")
        self.write(tornado.web.escape.xhtml_unescape(self.render_string("../static/js/locale.js")))

class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if not self.current_user:
            locales_dict = smarty.get_locales(self.locale)
            self.render("login.html", locales=locales_dict, selected=self.get_cookie("locale"))
        else:
            self.redirect("/")

    def post(self, *args, **kwargs):
        login = self.get_argument("login")
        login_response = self.users_manager.user_login(login, self.get_argument("password"))

        if not login_response["error"]:
            self.set_secure_cookie("login", login)

        self.write(login_response)

class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        self.users_manager.user_logout(self.current_user)
        self.clear_cookie("login")

class CreateCharacterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        character = self.db_manager.get_character(self.current_user)
        if not character:
        # no character - redirect to creation
            self.render("create_character.html", name=self.current_user, classes=get_classes(self.locale))
        else:
            self.redirect("/")

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        classID = self.get_argument("classID")
        # insert the new character
        self.db_manager.create_character(self.current_user, classID)

class DropCharacterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # remove the character from DB
        self.db_manager.remove_character(self.current_user)

class PollCharacterInfoHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.characters_manager.subscribe(self.current_user, self.on_action, self.locale)

    def on_action(self, action):
        if self.request.connection.stream.closed():
            return

        result = {}
        if action.type == 1:
            result = action.args
            result["team_div"] = self.render_string("create_team.html")
        elif action.type == 2:
            result["type"] = action.type
            result["team_div"] = self.render_string("team_info.html",
                user_name=self.current_user,
                team_name=action.args["team_name"],
                team_gold=action.args["team_gold"],
                members=action.args["members"])
        elif action.type == 3:
            result = action.args
            result["invitation_div"] = self.render_string("team_invitation.html",
                user_name=action.args["user_name"],
                team_name=action.args["team_name"])
        else:
            result = action.args

        def finish_request():
            if not self.request.connection.stream.closed():
                self.finish(result)

        tornado.ioloop.IOLoop.instance().add_callback(finish_request)

    def on_connection_close(self):
        self.characters_manager.unsubscribe(self.current_user)

class BattleBotHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        if self.get_argument("action") == 'join':
            self.battle_bot.user_join(self.current_user)
        elif self.get_argument("action") == 'leave':
            self.battle_bot.user_leave(self.current_user)
        elif self.get_argument("action") == 'turn do':
            self.battle_bot.user_turn(self.current_user, self.get_argument("turn_info"))
        elif self.get_argument("action") == 'turn cancel':
            self.battle_bot.user_turn_cancel(self.current_user)

class PollBotHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.battle_bot.subscribe(self.current_user, self.on_action, self.locale)

    def on_action(self, action):
        # Closed client connection
        if self.request.connection.stream.closed():
            return

        result = {}
        if action.type == 0:
            result = action.args
        elif action.type == 1 or action.type == 2:
            result = action.args
        elif action.type == 3 or action.type == 4 or action.type == 5:
            result["type"] = action.type
            if "turn_info" in action.args.keys():
                result["turn_info"] = action.args["turn_info"]
            result["div_action"] = self.render_string("div_action.html", actions=action.args["actions"], users=action.args["users"], spells=action.args["spells"])
        else:
            result = action.args

        def finish_request():
            if not self.request.connection.stream.closed():
                self.finish(result)

        tornado.ioloop.IOLoop.instance().add_callback(finish_request)

    def on_connection_close(self):
        self.battle_bot.unsubscribe(self.current_user)

class PollUsersHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.users_manager.subscribe(self.current_user, self.on_users_changed, self.locale)

    def on_users_changed(self, action):
        # Closed client connection
        if self.request.connection.stream.closed():
            return

        def finish_request():
            if not self.request.connection.stream.closed():
                self.finish(action.args)

        tornado.ioloop.IOLoop.instance().add_callback(finish_request)

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

        def finish_request():
            if not self.request.connection.stream.closed():
                self.finish(message)

        tornado.ioloop.IOLoop.instance().add_callback(finish_request)

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

class TeamHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        if self.get_argument("action") == "create":
            self.write(self.characters_manager.create_team(self.current_user, self.get_argument("team_name")))
        elif self.get_argument("action") == "promote":
            self.characters_manager.promote_user(self.current_user, self.get_argument("user_name"))
        elif self.get_argument("action") == "demote":
            self.characters_manager.demote_user(self.current_user, self.get_argument("user_name"))
        elif self.get_argument("action") == "remove":
            self.characters_manager.remove_user_from_team(self.current_user, self.get_argument("user_name"))
        elif self.get_argument("action") == "invite":
            self.write(self.characters_manager.invite_user_to_team(self.current_user, self.get_argument("user_name")))
        elif self.get_argument("action") == "confirm":
            self.characters_manager.user_join_team(self.current_user, self.get_argument("user_name"), self.get_argument("team_name"))
        elif self.get_argument("action") == "decline":
            pass
        elif self.get_argument("action") == "leave":
            self.characters_manager.user_leave_team(self.current_user)

def main():
    tornado.locale.load_gettext_translations("locale", "skirmish")
    http_server = tornado.httpserver.HTTPServer(SkirmishApplication())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()