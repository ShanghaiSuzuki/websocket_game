"""
登録画面のハンドラ
"""
import uuid

from lib.TornadoHandlers.BaseHandler import BaseHandler
from lib.DB.DBSingleton import DBSingleton, DBError


class RegisterHandler(BaseHandler):

    def get(self):
        self.render("register.html")

    def post(self):
        self.check_xsrf_cookie()
        username = self.get_argument('username')
        userpass = self.get_argument('userpass')
        country = self.get_argument("country")

        #簡単なチェック
        if len(username) > 7 or len(username) <1 or len(userpass) is not 4:
            message = "ユーザー名は１－７文字以内、パスは4桁"
            self.render("error.html",message=message)
            return

        if int(country) < 0 or int(country) > 1:
            message = "不正な国<br>"
            message += "country = " + str(country)
            self.render("error.html",message=message)
            return

        #キャラ登録
        db = DBSingleton()

        #初期位置は首都
        try:
            result = db.select("capital_col", "capital_row", table="country", where="country_id="+str(country))
        except DBError as e:
            self.render("error.html", message = e.message)
            return

        col = result[0][0]
        row = result[0][1]

        #id生成
        id = uuid.uuid4()

        #キャラ作成
        try:
            result = db.select("user_name", table="user", where="user_name=\"" + str(username) + "\"")
            print(len(result))
            if len(result) is not 0:
                self.render("error.html", message = u"既に同じ名前が登録されている")
                return

            db.insert(table="user",
                      user_id=id.hex,
                      user_pass=str(userpass),
                      user_name=str(username),
                      country_id=country,
                      col=col,row=row,
                      hp=10,mp=10,
                      at=10, df=10, mat=10, mdf=10,
                      ag=10, cha=10, led=10,
                      money=10000)
        except DBError as e:
            self.render("error.html", message = e.message)
            return

        self.redirect("login")

