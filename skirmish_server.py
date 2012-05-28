import functools
from tornado import web
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.database
import tornado.locale
from actions_manager import ActionsManager
from battle_manager import BattleManager
from db_manager import DBManager
import items_manager
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
            (r'/bot/battle', BattleBotHandler,),
            (r'/bot/poll', PollBotHandler,),
            (r'/users/poll', PollUsersHandler,),
            (r'/message/poll', PollMessageHandler,),
            (r'/info/poll', PollCharacterInfoHandler,),
            (r'/message/new', NewMessageHandler,),
            (r'/character', CharacterHandler,),
            (r'/shop', ShopHandler,),
            (r'/db', ItemsDBHandler,),
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

        self.actions_manager = ActionsManager()
        self.db_manager = DBManager(self.db, self.actions_manager)

        self.users_manager = UsersManager(self.db_manager, self.actions_manager)
        self.users_manager.start()

        self.battle_manager = BattleManager(self.actions_manager)

        self.characters_manager = CharactersManager(self.db_manager, self.actions_manager)
        self.messager = Messager()

        self.actions_manager.users_manager = self.users_manager
        self.actions_manager.characters_manager = self.characters_manager
        self.actions_manager.battle_manager = self.battle_manager

class BaseHandler(tornado.web.RequestHandler):
    @property
    def actions_manager(self):
        return self.application.actions_manager

    @property
    def characters_manager(self):
        return self.application.characters_manager

    @property
    def db_manager(self):
        return self.application.db_manager

    @property
    def users_manager(self):
        return self.application.users_manager

    @property
    def battle_manager(self):
        return self.application.battle_manager

    @property
    def messager(self):
        return self.application.messager

    def get_current_user(self):
        return self.get_secure_cookie("login")

    def get_user_locale(self):
        return tornado.locale.get(self.get_cookie("locale"))

    def get_user_location(self):
        return self.get_secure_cookie("location")

def user_online(method):
    """Decorate methods with this to check if user online and add if not"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user in self.actions_manager.online_users.keys():
            return method(self, *args, **kwargs)
        else:
            return
    return wrapper

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        character = self.db_manager.get_character(self.current_user)
        if not character: # no such user - redirect to creation
            self.render("create_character.html", name=self.current_user, classes=get_classes(self.locale))
        else:
            if not self.current_user in self.actions_manager.online_users.keys():
                self.actions_manager.add_online_user(self.current_user, self.locale)
            self.db_manager.update_character(self.current_user)
            self.actions_manager.user_enter(self.current_user)

            self.render("skirmish.html",
                login=self.current_user,
                substance=smarty.get_substance_name(character.classID, self.locale),
                shop=items_manager.get_shop(self.locale))

class StaticJSHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "text/javascript")
        self.write(tornado.web.escape.xhtml_unescape(self.render_string("../static/js/locale.js")))

class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if not self.current_user:
            self.render("login.html", locales=smarty.locales, selected=self.locale)
        else:
            self.redirect("/")

    def post(self, *args, **kwargs):
        login = self.get_argument("login")
        login_response = self.users_manager.user_login(login, self.get_argument("password"))

        if not login_response["error"]:
            self.set_secure_cookie("login", login)

        self.write(login_response)

class CreateCharacterHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        classID = self.get_argument("classID")
        # insert the new character
        self.db_manager.create_character(self.current_user, classID)

class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    def post(self, *args, **kwargs):
        self.users_manager.user_logout(self.current_user)
        self.clear_cookie("login")

class CharacterHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    def post(self, *args, **kwargs):
        if self.get_argument("action") == 'drop':
            self.db_manager.remove_character(self.current_user)
        elif self.get_argument("action") == 'change_location':
            self.users_manager.change_location(self.current_user, self.get_argument("location"))
        elif self.get_argument("action") == 'put_on':
            if not self.characters_manager.put_on_item(self.current_user, self.get_argument("thing_id")):
                self.write("false")
        elif self.get_argument("action") == "create_team":
            self.write(self.characters_manager.create_team(self.current_user, self.get_argument("team_name")))
        elif self.get_argument("action") == "promote_team":
            self.characters_manager.promote_user(self.current_user, self.get_argument("user_name"))
        elif self.get_argument("action") == "demote_team":
            self.characters_manager.demote_user(self.current_user, self.get_argument("user_name"))
        elif self.get_argument("action") == "remove_team":
            self.characters_manager.remove_user_from_team(self.current_user, self.get_argument("user_name"))
        elif self.get_argument("action") == "invite_team":
            self.write(self.characters_manager.invite_user_to_team(self.current_user, self.get_argument("user_name")))
        elif self.get_argument("action") == "confirm_team":
            self.characters_manager.user_join_team(self.current_user, self.get_argument("user_name"), self.get_argument("team_name"))
        elif self.get_argument("action") == "decline_team":
            pass
        elif self.get_argument("action") == "leave_team":
            self.characters_manager.user_leave_team(self.current_user)
        elif self.get_argument("action") == "learn_spell":
            self.characters_manager.learn_spell(self.current_user, self.get_argument("spell_id"))

class PollCharacterInfoHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @user_online
    def post(self, *args, **kwargs):
        self.characters_manager.subscribe(self.current_user, self.on_action)

    def on_action(self, action):
        if self.request.connection.stream.closed():
            return

        result = {}
        if action.type == 2:
            result["type"] = action.args["type"]
            result["spells_div"] = self.render_string("spells_table.html", spells=action.args["spells"], spells_to_learn=action.args["spells_to_learn"])
        elif action.type == 3:
            result = action.args
            result["team_div"] = self.render_string("create_team.html")
        elif action.type == 4:
            result["type"] = action.type
            result["team_div"] = self.render_string("team_info.html",
                user_name=self.current_user,
                team_name=action.args["team_name"],
                team_gold=action.args["team_gold"],
                members=action.args["members"])
        elif action.type == 5:
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
    @user_online
    def post(self, *args, **kwargs):
        if self.get_argument("action") == 'join':
            self.battle_manager.user_join(self.current_user)
        elif self.get_argument("action") == 'leave':
            self.battle_manager.user_leave(self.current_user)
        elif self.get_argument("action") == 'turn do':
            self.battle_manager.user_turn(self.current_user, self.get_argument("turn_info"))
        elif self.get_argument("action") == 'turn cancel':
            self.battle_manager.user_turn_cancel(self.current_user)

class PollBotHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.battle_manager.subscribe(self.current_user, self.on_action)

    def on_action(self, action):
        # Closed client connection
        if self.request.connection.stream.closed():
            return

        result = {}
        if action.type == 5 or action.type == 6 or action.type == 7:
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
        self.battle_manager.unsubscribe(self.current_user)

class PollUsersHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.users_manager.subscribe(self.current_user, self.on_users_changed)

    def on_users_changed(self, action):
        # Closed client connection
        if self.request.connection.stream.closed():
            return

        result = action.args

        def finish_request():
            if not self.request.connection.stream.closed():
                self.finish(result)

        tornado.ioloop.IOLoop.instance().add_callback(finish_request)

    def on_connection_close(self):
        self.users_manager.unsubscribe(self.current_user)

class PollMessageHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
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
    @user_online
    def post(self, *args, **kwargs):
        message = {
            "from": self.current_user,
            "to": self.get_argument("to"),
            "body": self.get_argument("body"),
            }
        self.messager.new_message(message)

class ShopHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    def post(self, *args, **kwargs):
        if self.get_argument("action") == 'get_item':
            item = items_manager.get_item(int(self.get_argument("item_id")), self.locale)
            self.write(self.render_string("item_description.html",
                item=item,
                group_name=items_manager.get_item_group_name(item.type, self.locale),
                buy_button=True,
                can_buy=(self.users_manager.online_users[self.current_user].character.gold >= item.price)))
        elif self.get_argument("action") == 'buy_item':
            self.characters_manager.buy_item(self.current_user, self.get_argument("item_id"))

class ItemsDBHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    def post(self, *args, **kwargs):
        if self.get_argument("action") == 'get_item':
            item = items_manager.get_item(int(self.get_argument("item_id")), self.locale)
            self.write(self.render_string("item_description.html",
                item=item,
                group_name=items_manager.get_item_group_name(item.type, self.locale),
                buy_button=False,
                can_buy=False))

def main():
    tornado.locale.load_gettext_translations("locale", "skirmish")
    http_server = tornado.httpserver.HTTPServer(SkirmishApplication())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()