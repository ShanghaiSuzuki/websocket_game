from lib.DB.DBSingleton import DBSingleton, DBError
from lib.TornadoHandlers.BJSocketHandler import BJSocketHandler
from lib.DB import event_controller, player_controller, hexgrid_controller, division_controller
from lib import GameMain
from lib.util import BJTime
from lib.TornadoHandlers.BJSocketHandler.notify_move_player import notify_move_player
import logging


class EventDomestic():
    """
    行軍イベント
    """


    def __init__(self, event_record):

        # レコード
        self._event_record = event_record

        # ロガー
        self._logger = logging.getLogger(__name__)

    def run(self):
        """
        内政をする
        :return: 成功 ? True : False
        """

        self._logger.debug("enter EventDomestic run")
        self._logger.debug("event_record=", self._event_record)


        # 例外処理用
        user_id = None
        division_id = None
        try:
            # デコード
            if self._decode_recode() is False:
                raise Exception("デコード失敗")
                return False

            # プレイヤー、部隊情報
            player_info = player_controller.get_playerinfo_by_id(self._user_id)
            division_info = division_controller.get_division_info(self._division_id)


            # 内政中でないならキャンセル(本来はイベントレコード自体がキャンセルされるべき
            if player_info["status"] != "domestic":
                raise Exception("プレイヤーの状態がdomesticではない")
                return

            # 移動中でないならキャンセル(本来はイベントレコード自体がキャンセルされるべき）
            if division_info["status"] != "domestic":
                raise Exception("部隊の状態がdomesticではない")
                return

            # エラーに備えて本処理前にプレイヤーと部隊の状態を初期化する
            player_controller.update_user_status(self._user_id, "ready")
            division_controller.update_division_status(self._division_id, "ready")

            # 現在時刻
            now = BJTime.get_time_now()

            # ヘックス情報
            hex = hexgrid_controller.get_hexinfo(self._domestic_col, self._domestic_row)

            # 対象ヘックスの国籍が変わっていれば失敗
            if hex["country_id"] != player_info["country_id"]:
                BJSocketHandler.BJSocketHandler.send_member_by_id(player_info["user_id"],
                                                                  {"event" : "cancel",
                                                                   "data" : {"title" : "内政キャンセル",
                                                                              "reason" : "対象ヘックスの国籍が違う"}})
                return

            # 内政実行
            # TODO : ステータスなどに合わせた変化

            gm = GameMain.GameMain()
            message = "("+str(self._domestic_col)+","+str(self._domestic_row)+")\n " # 結果メッセージ

            isSuccessed = False

            # 最大値増量
            if self._type == "foster_food":
                new_food = gm.get_affair().get_op_food_lv() + hex["food"]
                if not hexgrid_controller.update_hex(hex["col"], hex["row"], food = new_food):
                    message = message + "エラー。農業生産失敗"
                else:
                    message = message + "農業生産　" + str(hex["food"]) + " → " + str(new_food)
                    isSuccessed = True
            elif self._type == "foster_money":
                new_money = gm.get_affair().get_op_food_lv() + hex["money"]
                if not hexgrid_controller.update_hex(hex["col"], hex["row"], money = new_money):
                    message = message + "エラー。商業生産失敗"
                else:
                    message = message + "商業生産　" + str(hex["money"]) + " → " + str(new_money)
                    isSuccessed = True

            # 徴税
            elif self._type == "get_food":
                new_food = hex["food"] + division_info["food"]
                if not division_controller.update_division(division_info["division_id"], food=new_food):
                    message = message + "エラー。農業徴税失敗"
                else:
                    message = message + "領地から" + str(hex["food"]) + "の食糧を部隊に徴税した"
                    isSuccessed = True
            elif self._type == "get_money":
                new_money = hex["money"] + division_info["money"]
                if not division_controller.update_division(division_info["division_id"], money=new_money):
                    message = message + "エラー。商業徴税失敗"
                else:
                    message = message + "領地から" + str(hex["money"]) + "の資金を部隊に徴税した"
                    isSuccessed = True

            # 内政に失敗していればメッセージ送信
            if not isSuccessed:
                BJSocketHandler.BJSocketHandler.send_member_by_id(player_info["user_id"],
                                                                  {"event" : "cancel",
                                                                   "data" : {"title" : "内政失敗",
                                                                              "reason" : "不明な内政種類"}})
                return

            # 内政に成功。結果をプレイヤーに通知
            BJSocketHandler.BJSocketHandler.send_member_by_id(player_info["user_id"],
                                                              {"event" : "notify",
                                                               "data" : {"title" : "内政成功",
                                                                          "message" : message}})
        except DBError as e:
            logging.error("EventMove::run: caught DBError: " + e.message)

        except Exception as e:

            # 状態を初期化しておく
            player_controller.update_user_status(user_id, "ready")
            division_controller.update_division_status(division_id, "ready")

            logging.error(e)

            # プレイヤーにエラーを通知
            payload = { "event" : "cancel",
                        "data" : { "title" : "内政キャンセル",
                                    "reason" : "内部エラー"}}
            BJSocketHandler.BJSocketHandler.send_member_by_id(self._user_id, payload)

    def _decode_recode(self):
        """
        イベントレコードをデコードし、必要なデータを回収する
        :param event_record:
        :return: 成功 ? True : False
        """

        # イベントレコードがEventMoveのコンストラクタでセットされていなければ失敗
        if self._event_record is None:
            self._logger.error(u"イベントレコードを持たないまま呼び出された")
            return False

        try:

            # record[object]から主体ユーザーID
            self._user_id = self._event_record["object"]

            # データ部デコード
            data = self._event_record["data"].split(",")

            self._division_id = data[0]
            self._domestic_col = data[1]
            self._domestic_row = data[2]
            self._type = data[3]

            return True

        except Exception as e:
            self._logger.error(u"不正な形式のレコード", e.message, self._event_record)
            return False

        assert False

    @classmethod
    def create_recode(cls, user_id, division_id, col, row, type, datetime):
        """
        レコード作成
        :param user_id: 内政するユーザー
        :param division_id: 内政する部隊
        :param dest_col: 内政地col
        :param dest_row: 内政地row
        :param type: 内政の種類
        :param datetime: 終了時刻
        :return: event_record[event_id, ...]
        """

        # データ部
        # "division_id,col,row"
        data = str(division_id) + "," + str(col) + "," + str(row) + "," + str(type)

        event = event_controller.create_event(datetime=datetime,
                                              object=user_id,
                                              subject="none",
                                              event_name="domestic",
                                              data=data)

        return event