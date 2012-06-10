import functools
from tornado import web
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.database
import tornado.locale
from users_holder import UsersHolder
from battle_manager import BattleManager
from db_manager import DBManager
import items_manager
import smarty
import spells_manager
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
            (r'/create', CreateCharacterHandler,),
            (r'/poll', PollBotHandler,),
            (r'/message/poll', PollMessageHandler,),
            (r'/action', ActionHandler,),
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

        self.users_holder = UsersHolder()
        self.db_manager = DBManager(self.db, self.users_holder)
        self.characters_manager = CharactersManager(self.db_manager, self.users_holder)
        self.battle_manager = BattleManager(self.users_holder, self.db_manager, self.characters_manager)

        self.users_manager = UsersManager(self.db_manager, self.users_holder, self.battle_manager)
        self.users_manager.start()

        self.messager = Messager()

        self.users_holder.users_manager = self.users_manager
        self.users_holder.characters_manager = self.characters_manager
        self.users_holder.battle_manager = self.battle_manager

class BaseHandler(tornado.web.RequestHandler):
    @property
    def users_holder(self):
        return self.application.users_holder

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
        if self.current_user in self.users_holder.online_users.keys():
            return method(self, *args, **kwargs)
        else:
            return
    return wrapper

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # there is such user in db, double check after authentication
        # add bans, etc here
        if self.db_manager.get_user(self.current_user):
            character = self.db_manager.get_character(self.current_user)
            if not character: # no such user - redirect to creation
                self.render("create_character.html",
                    name=self.current_user,
                    classes=smarty.get_classes(self.locale),
                    races=smarty.get_races(self.locale))
            else:
                if not self.current_user in self.users_holder.online_users.keys():
                    self.users_manager.add_online_user(self.current_user, self.locale)
                if self.users_holder.online_users[self.current_user].state != 1:
                    self.db_manager.update_character(self.current_user)
                self.users_holder.user_enter(self.current_user)

                database = items_manager.get_all(self.locale)
                database.update(spells_manager.get_all_spells(self.locale))
                self.render("skirmish.html",
                    location=self.users_holder.online_users[self.current_user].location,
                    substance=smarty.get_substance_name(character.class_id, self.locale),
                    shop=items_manager.get_shop(self.locale),
                    database=database,
                    locations=smarty.get_locations(self.locale))
        else:
            self.clear_all_cookies()
            self.redirect("/")

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
        # insert the new character
        self.db_manager.create_character(self.current_user, self.get_argument("race_id"), self.get_argument("class_id"))

class ActionHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    def post(self, *args, **kwargs):
        if self.get_argument("action") == 'drop':
            self.db_manager.remove_character(self.current_user)
        elif self.get_argument("action") == 'change_location':
            self.battle_manager.user_leave(self.current_user)
            self.users_manager.change_location(self.current_user, int(self.get_argument("location")))
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
        elif self.get_argument("action") == 'join':
            self.battle_manager.user_join(self.current_user)
        elif self.get_argument("action") == 'leave':
            self.battle_manager.user_leave(self.current_user)
        elif self.get_argument("action") == 'turn_do':
            self.battle_manager.user_turn(self.current_user, self.get_argument("turn_info"))
        elif self.get_argument("action") == 'turn_cancel':
            self.battle_manager.user_turn_cancel(self.current_user)
        elif self.get_argument("action") == 'logout':
            self.users_manager.user_logout(self.current_user)
            self.clear_cookie("login")
        elif self.get_argument("action") == 'new_message':
            message = {
                "from": self.current_user,
                "to": self.get_argument("to"),
                "body": self.get_argument("body"),
                }
            self.messager.new_message(message)
        elif self.get_argument("action") == 'shop_get_item':
            item = items_manager.get_item(int(self.get_argument("item_id")), self.locale)
            self.write(self.render_string("item_description.html",
                item=item,
                group_name=items_manager.get_item_group_name(item.type, self.locale),
                buy_button=True,
                can_buy=(self.users_manager.online_users[self.current_user].character.gold >= item.price)))
        elif self.get_argument("action") == 'buy_item':
            self.characters_manager.buy_item(self.current_user, self.get_argument("item_id"))
        elif self.get_argument("action") == 'db_get_item':
            id = int(self.get_argument("item_id"))
            if id >= items_manager.build_id(10, 0) and id < items_manager.build_id(18, 0):
                spell = spells_manager.get_spell(id, self.locale)
                self.write(self.render_string("spell_description.html",
                    spell=spell,
                    group_name=smarty.get_class_name(spell.class_id, self.locale),
                    substance_name=smarty.get_substance_name(spell.class_id, self.locale)))
            else:
                item = items_manager.get_item(id, self.locale)
                self.write(self.render_string("item_description.html",
                    item=item,
                    group_name=items_manager.get_item_group_name(item.type, self.locale),
                    buy_button=False,
                    can_buy=False))

class PollBotHandler(BaseHandler):
    @tornado.web.authenticated
    @user_online
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self.users_holder.online_users[self.current_user].set_callback(self.on_action)

    def on_action(self, action):
        # Closed client connection
        if self.request.connection.stream.closed():
            return

        result = {}
        if action.type == 1:
            result["type"] = action.type
            result["div_action"] = self.render_string("div_action.html", actions=action.args["actions"], users=action.args["users"], spells=action.args["spells"])
        elif action.type == 202:
            result["type"] = action.args["type"]
            result["spells_div"] = self.render_string("spells_table.html",
                spells=action.args["spells"],
                spells_to_learn=action.args["spells_to_learn"],
                substance_name=action.args["substance_name"])
        elif action.type == 203:
            result = action.args
            result["team_div"] = self.render_string("create_team.html")
        elif action.type == 204:
            result["type"] = action.type
            result["team_div"] = self.render_string("team_info.html",
                user_name=self.current_user,
                team_name=action.args["team_name"],
                team_gold=action.args["team_gold"],
                members=action.args["members"])
        elif action.type == 205:
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
        if self.current_user in self.users_holder.online_users:
            self.users_holder.online_users[self.current_user].set_callback(None)

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

def main():
    tornado.locale.load_gettext_translations("locale", "skirmish")
    http_server = tornado.httpserver.HTTPServer(SkirmishApplication())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()