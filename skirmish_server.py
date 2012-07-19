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

        self.users_manager = UsersManager(self.db_manager, self.users_holder, self.characters_manager, self.battle_manager)
        self.users_manager.start()

        self.messager = Messager(self.users_holder.online_users, self.users_holder.location_users)

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
                self.users_manager.on_user_enter(self.current_user, self.locale)
# prepare divUsers
                user = self.users_holder.online_users[self.current_user]
                online_team_users = dict()
                if user.character.team_name:
                    for online_user in self.users_holder.online_users.values():
                        if online_user.character.team_name == user.character.team_name:
                            online_team_users[online_user.user_name] = online_user

                location_team_users = dict()
                for online_user in online_team_users.values():
                    if online_user.location == user.location and user.user_name != online_user.user_name:
                        location_team_users[online_user.user_name] = online_user

                div_users = self.render_string("div_users.html",
                    skirmish_users=self.battle_manager.battle_bots[user.location].battle_users,
                    location_team_users=location_team_users,
                    online_team_users=online_team_users,
                    location_users=self.users_holder.location_users[user.location]
                    )

# prepare skirmish.html
                database = dict()
                database["Items"] = items_manager.get_all(self.locale)
                database["Spells"] = spells_manager.get_all_spells(self.locale)
                locations = smarty.get_locations(self.locale)
                locations.insert(0, locations.pop(self.users_holder.online_users[self.current_user].location))
                self.render("skirmish.html",
                    substance=smarty.get_substance_name(character.class_id, self.locale),
                    shop={"Items" : items_manager.get_shop(self.locale)},
                    database=database,
                    locations=locations,
                    div_users=div_users)
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
        if self.get_argument("action") == 'login':
            login = self.get_argument("login")
            login_response = self.users_manager.user_login(login, self.get_argument("password"))
            if not login_response["error"]:
                self.set_secure_cookie("login", login)
            self.write(login_response)
        elif self.get_argument("action") == 'logout':
            self.users_manager.user_logout(self.current_user)
            self.clear_cookie("login")

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
            if not self.characters_manager.put_on_item(self.current_user, self.get_argument("item_id")):
                self.write("false")
        elif self.get_argument("action") == 'take_off':
            self.characters_manager.take_off_item(self.current_user, self.get_argument("item_id"))
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
        elif self.get_argument("action") == 'new_message':
            message = {
                "from": self.current_user,
                "message_type": self.get_argument("message_type"),
                "body": self.get_argument("body")
                }
            if self.get_argument("message_type") == "private":
                message["to"] = self.get_argument("to")
            self.messager.new_message(self.current_user, message)
        elif self.get_argument("action") == 'shop_get_item':
            item_id = int(self.get_argument("item_id"))
            self.write(self.render_item_description(item_id, True))
        elif self.get_argument("action") == 'db_get_item':
            item_id = int(self.get_argument("item_id"))
            if item_id >= items_manager.build_id(10, 0) and item_id < items_manager.build_id(18, 0):
                spell = spells_manager.get_spell(item_id, self.locale)
                self.write(self.render_string("spell_description.html",
                    spell=spell,
                    group_name=smarty.get_class_name(spell.class_id, self.locale),
                    substance_name=smarty.get_substance_name(spell.class_id, self.locale)))
            else:
                self.write(self.render_item_description(item_id, False))
        elif self.get_argument("action") == 'buy_item':
            self.characters_manager.buy_item(self.current_user, self.get_argument("item_id"))
        elif self.get_argument("action") == 'open_chat':
            self.users_manager.open_chat(self.current_user, self.get_argument("user_name"), self.get_argument("message", ""))
        elif self.get_argument("action") == 'close_chat':
            self.users_manager.close_chat(self.current_user, self.get_argument("user_name"))
        elif self.get_argument("action") == 'change_gold_tax':
            self.characters_manager.change_gold_tax(self.current_user, self.get_argument("strategy"))
        elif self.get_argument("action") == 'change_gold_sharing':
            self.characters_manager.change_gold_sharing(self.current_user, self.get_argument("strategy"))
        elif self.get_argument("action") == 'change_experience_sharing':
            self.characters_manager.change_experience_sharing(self.current_user, self.get_argument("strategy"))

    def render_item_description(self, item_id, buy_button=True):
        item = items_manager.get_item(item_id, self.locale)
        required = item.required_stats.get_required(self.locale)
        bonus = item.bonus_stats.get_bonus(self.locale)
        classes = item.classes.get_class_names(self.locale)
        can_buy = False
        if buy_button:
            can_buy = (self.users_manager.online_users[self.current_user].character.gold >= item.price)
        return self.render_string("item_description.html",
            item=item,
            group_name=items_manager.get_item_group_name(item.type, self.locale),
            buy_button=buy_button,
            can_buy=can_buy,
            required=", ".join("{0} {1}".format(stat_name, str(required[stat_name])) for stat_name in required.keys()),
            bonus=", ".join("{0} {1}".format(stat_name, str(bonus[stat_name])) for stat_name in bonus.keys()),
            classes=", ".join(classes))

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
            result["div_action"] = self.render_string("div_action.html", actions=action.args["actions"], spells=action.args["spells"])
        elif action.type == 10: # add skirmish user
            result["type"] = action.type
            result["user_name"] = action.args["user"].user_name
            result["user_label"] = self.render_string("user_label.html",
                type=0,
                user=action.args["user"],
                visible=True)
        elif action.type == 101: # add location user
            result["type"] = action.type
            result["user_name"] = action.args["user"].user_name
            result["user_label"] = self.render_string("user_label.html",
                type=action.args["user_type"],
                user=action.args["user"],
                visible=True)
        elif action.type == 104: # add online team user
            result["type"] = action.type
            result["user_name"] = action.args["user"].user_name
            result["user_label"] = self.render_string("user_label.html",
                type=1,
                user=action.args["user"],
                visible=True)
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
            team_info = action.args["team_info"]
            team_name = team_info.team_name
            gold_tax = smarty.get_gold_tax(self.locale)
            gold_tax.insert(0, gold_tax.pop(team_info.gold_tax))
            gold_sharing = smarty.get_gold_sharing(self.locale)
            gold_sharing.insert(0, gold_sharing.pop(team_info.gold_sharing))
            experience_sharing = smarty.get_experience_sharing(self.locale)
            experience_sharing.insert(0, experience_sharing.pop(team_info.experience_sharing))
            result["team_div"] = self.render_string("team_info.html",
                user_name=self.current_user,
                team_name=team_name,
                team_gold=team_info.gold,
                members=action.args["members"],
                gold_sharing=gold_sharing,
                experience_sharing=experience_sharing,
                gold_tax=gold_tax)
            result["team_name"] = team_name
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

def main():
    tornado.locale.load_gettext_translations("locale", "skirmish")
    http_server = tornado.httpserver.HTTPServer(SkirmishApplication())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()