import random
import string
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.database
import os

__author__ = 'PavelP'

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

class SkirmishApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler,),
            (r'/login', LoginHandler,),
            (r'/logout', LogoutHandler,),
            (r'/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__))))
        ]
        settings = {
            "cookie_secret" : "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "login_url": "/login",
            "xsrf_cookies": True,
            }

        tornado.web.Application.__init__(self, handlers, **settings)

        # have one global connection to the application db across all handlers
        self.db = tornado.database.Connection(
            host="127.0.0.1:3306", database="users",
            user="root", password="passw0rd")

        self.online_users = dict()

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie("login")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render("skirmish.html", login=self.current_user)

class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if not self.current_user:
            self.render("login.html")
        else:
            self.render("skirmish.html", login=self.current_user)

    def post(self, *args, **kwargs):
        login_response = {
            'error': False,
            'msg': ''
        }

        login = self.get_argument("login")
        password = self.get_argument("password")

        # uncomment in case db should be created - first start
#        self.db.execute("create table if not exists users (id integer(11) primary key not null auto_increment unique, login text, password text)")
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
        self.clear_cookie("login")

def main():
    http_server = tornado.httpserver.HTTPServer(SkirmishApplication())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()