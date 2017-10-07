import tornado.web

from lib.TornadoHandlers.BaseHandler import BaseHandler


class MainHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        username = self.get_current_user()
        self.render('Auth/index.html', username = username)
