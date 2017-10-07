import tornado.web
import logging


class BaseHandler(tornado.web.RequestHandler):

    cookie_user_id = "user_id"

    def get_current_user(self):
        user_id = self.get_secure_cookie(self.cookie_user_id)
        if not user_id: return None
        return tornado.escape.utf8(user_id)

    def set_current_user(self, user_id):
        self.set_secure_cookie(self.cookie_user_id, tornado.escape.utf8(user_id))

    def clear_current_user(self):
        self.clear_cookie(self.cookie_user_id)

    # クライアントのブラウザがスマホならTrue
    def is_smartphone(self):

        ua = self.request.headers["User-Agent"].lower()
        print(ua)
        if ua.find("iphone") > 0 and ua.find("ipad") < 0 \
            or ua.find("android") > 0 and ua.find("mobi") > 0\
            or ua.find("windows") > 0 and ua.find("phone") > 0:
            return True
        return False

