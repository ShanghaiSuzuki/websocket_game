import tornado.escape
import tornado.websocket
import logging

from lib.TornadoHandlers.BJSocketHandler.echo import echo
from lib.TornadoHandlers.BJSocketHandler.move import *
from lib.TornadoHandlers.BJSocketHandler.init_hexgrid import *
from lib.TornadoHandlers.BJSocketHandler.init_bbs_country import *
from lib.TornadoHandlers.BJSocketHandler.update_bbs_country import *
from lib.DB import player_controller


class BJSocketHandler(tornado.websocket.WebSocketHandler):
    """
    メインハンドラ
    """

    # 現在通信中のメンバー
    members = {}

    # 個別のハンドラを登録
    handlers = {"echo" : echo,
                "move_query" : move_query,
                "move_request" : move_request,
                "init_hexgrid" : init_hexgrid,
                "init_bbs_country" : init_bbs_country,
                "write_bbs_country" : write_bbs_country}

    def open(self):
        #TODO: トークン付与

        user_id= self.get_secure_cookie("user_id").decode('utf-8')
        country = None

        try:
            player = player_controller.get_playerinfo_by_id(user_id)

            if player["country_id"] is None:
                raise DBError(u"国IDが設定されていない。")

            if player["visibility"] is None:
                raise DBError(u"可視権が設定されていない")

        except DBError as e:
            self.on_error(u"国が特定できなかった。" + e.message)

        BJSocketHandler.members[user_id] = {"socket" : self,
                                            "country_id" : player["country_id"],
                                            "visibility" : player["visibility"]}
        logging.debug(user_id + " connected")

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        #TODO: トークン確認・再発行

        self.dispatch(message)

    def on_close(self):

        #TODO: トークン削除
        user_id= self.get_secure_cookie("user_id").decode('utf-8')
        logging.debug("connection with " + user_id + " was closed")
        del BJSocketHandler.members[user_id]

    def send_error(self, message):
        """
        インスタンスのプレイヤーにエラーメッセージを送信する
        :param message: メッセージ
        :return:
        """
        user_id = self.get_secure_cookie("user_id").decode('utf-8')
        logging.error("In connection with " + user_id + "\nmessage = " + str(message))
        payload = { "event" : "error", "data" : str(message)}
        self.send_you(payload)

    # TODO: 非同期処理実装
    @classmethod
    def send_all(cls, raw_dict_data):
        """
        通信中の全プレイヤーにデータを送信する
        :param raw_dict_data: { event, data }
        :return:
        """

        for key in cls.members:
            print(key)

        #JSONにフォーマット
        payload = tornado.escape.json_encode(raw_dict_data)
        for key in BJSocketHandler.members:
            BJSocketHandler.member[key]["socket"].write_message(payload)

    def send_you(self, raw_dict_data):
        """
        自身に送信
        :param raw_dict_data: {event, data}
        :return:
        """
        payload = tornado.escape.json_encode(raw_dict_data)
        self.write_message(payload)

    @classmethod
    def register_event_handler(cls, event, handler):
        """イベントとハンドラ登録"""
        cls.handlers[event] = handler

    # TODO: 非同期処理実装
    @classmethod
    def send_member_by_country(cls, raw_dict_data, country_id):
        """
        指定された国IDを持つ接続中のプレイヤーに送信
        :param raw_dict_data: {送信するデータ}
        :param country_id: 国ID
        :return:
        """

        payload = tornado.escape.json_encode(raw_dict_data)
        for key in cls.members:
            if cls.members[key]["country_id"] is country_id:
                cls.members[key]["socket"].write_message(payload)

    # TODO: 非同期処理実装
    @classmethod
    def send_member_by_visibility(cls, raw_dict_data, visibility):
        """
        指定された可視権を持つ接続中のプレイヤーに送信
        :param raw_dict_data: {送信するデータ}
        :param visibility: 可視権
        :return:
        """
        print("send_mem_by_vis", visibility)
        payload = tornado.escape.json_encode(raw_dict_data)
        print("payload", payload)
        for key in cls.members:
            print(key, "vis", cls.members[key]["visibility"], "visb", visibility)
            print("typeof cls",type(cls.members[key]["visibility"]))
            print("typeof vis",type(visibility))
            print(cls.members[key]["visibility"] == visibility)
            if cls.members[key]["visibility"] == visibility:
                print(cls.members[key])
                cls.members[key]["socket"].write_message(payload)

    # TODO: 非同期処理実装
    @classmethod
    def send_member_by_id(cls, user_id, raw_dict_data):
        """
        user_idで指定したプレイヤーが接続中なら送信
        :param raw_dict_data:{送信するデータ}
        :return: 送信成功 ? True : False
        """
        payload = tornado.escape.json_encode(raw_dict_data)
        if cls.members[user_id]:
            cls.members[user_id]["socket"].write_message(payload)
            return True
        else:
            return False

    def dispatch(self, message):
        """eventから適切なハンドラを実行"""

        content = tornado.escape.json_decode(message)
        if(BJSocketHandler.handlers[content["event"]]):

            try:
                #ハンドリング
                BJSocketHandler.handlers[content["event"]](BJSocketHandler, self, content["data"])

            except Exception as e:
                payload = tornado.escape.json_encode(
                { "event": "error", "data" : u"クライアントから送られてきたイベントのハンドラが無かったため、処理出来なかった。 " + content["event"]})
                print(e)
                self.write_message(payload)
                self.close()

        #ハンドラがなければエラー
        else:
            payload = tornado.escape.json_encode(
                { "event": "error", "data" : "couldn't find a handle for event : " + content["event"] })
            self.write_message(payload)



