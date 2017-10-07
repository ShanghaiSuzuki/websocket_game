import tornado.web
from lib.TornadoHandlers.BaseHandler import BaseHandler
from lib.DB.DBSingleton import DBSingleton, DBError
from lib.DB.player_controller import *


class LoginHandler(BaseHandler):

    def get(self):
        self.render('login.html')

    def post(self):
        self.check_xsrf_cookie()
        username = self.get_argument('username')
        userpass = self.get_argument('userpass')

        # 認証
        db = DBSingleton()
        user_info = None
        user_id = None
        try:
            user_id = get_userid_by_username(username)
            user_info = get_playerinfo_by_id(user_id)

        except Exception as e:
            logging.error(e)
            self.render("error.html", message="DBエラー")
            return

        if user_info["user_pass"] == userpass:
            self.set_current_user(tornado.escape.utf8(user_id))
            self.redirect("/index")
        else:
            self.render("error.html", message="ユーザー名とパスワードが一致しない")
            return


class LogoutHandler(BaseHandler):

    def post(self):
        self.clear_current_user()
        self.redirect("/")



