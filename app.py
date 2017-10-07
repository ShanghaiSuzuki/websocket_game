import logging
import os

import tornado.httpserver
import tornado.ioloop
import tornado.websocket
from tornado.web import url

from lib.TornadoHandlers.Auth.MainHandler import MainHandler
from lib.TornadoHandlers.BJSocketHandler.BJSocketHandler import BJSocketHandler
from lib.TornadoHandlers.LoginHandlers import LoginHandler
from lib.TornadoHandlers.LoginHandlers import LogoutHandler
from lib.TornadoHandlers.RegisterHandler import RegisterHandler
from lib.TornadoHandlers.TopHandler import TopHandler
from lib.GameMain import GameMain


class Application(tornado.web.Application):
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        tornado.web.Application.__init__(self,
                                         [
                                             url(r'/', TopHandler, name="top"),
                                             url(r'/index', MainHandler, name='index'),
                                             url(r'/login', LoginHandler, name="login"),
                                             url(r'/logout', LogoutHandler, name="logout"),
                                             url(r'/bjsocket', BJSocketHandler, name="bjsocket"),
                                             url(r'/register', RegisterHandler, name="register")
                                         ],
                                         template_path=os.path.join(BASE_DIR, 'template'),
                                         static_path=os.path.join(BASE_DIR, 'static'),
                                         login_url="login",
                                         cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
                                         debug=True
                                         )


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s: %(module)s: %(funcName)s: line %(lineno)d: %(message)s")


    gm = GameMain()
    gm.run()

    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
