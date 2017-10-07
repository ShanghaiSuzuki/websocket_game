from lib.TornadoHandlers.BaseHandler import BaseHandler


class TopHandler(BaseHandler):

    def get(self):
        self.render('top.html')
