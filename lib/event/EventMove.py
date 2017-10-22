from lib.DB.DBSingleton import DBSingleton, DBError
from lib.TornadoHandlers.BJSocketHandler import BJSocketHandler
from lib.DB import event_controller, player_controller, hexgrid_controller, division_controller
from lib.util import BJTime
from lib.TornadoHandlers.BJSocketHandler import notify_move_player
from datetime import datetime
import logging


class EventMove():
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
        プレイヤーを移動させる
        終了後はmove_playerイベントを送信する
        :return: 成功 ? True : False
        """

        self._logger.debug("enter run")
        self._logger.debug("event_record=", self._event_record)


        try:
            # デコード
            if self._decode_recode() is False:
                raise Exception("デコード失敗")
                return False

            # プレイヤー情報
            player = player_controller.get_playerinfo_by_id(self._user_id)
            moving_player_info = { "id" : player["user_id"],
                                   "ex_col" : player["col"],
                                   "ex_row" : player["row"],
                                   "new_col" : self._dest_col,
                                   "new_row" : self._dest_row,
                                   "icon" : player["icon"]}

            # 移動中でないならキャンセル(本来はイベントレコード自体がキャンセルされるべき
            if player["status"] != "moving":
                raise Exception("プレイヤーの状態がreadyではない")
                return

            # 部隊情報
            division = division_controller.get_division_info(player["division_id"])

            # 移動中でないならキャンセル(本来はイベントレコード自体がキャンセルされるべき）
            if division["status"] != "moving":
                raise Exception("部隊の状態がreadyではない")
                return

            # エラーに備えて本処理前にプレイヤーと部隊の状態を初期化する
            player_controller.update_user_status(self._user_id, "ready")
            division_controller.update_division_status(self._division_id, "ready")

            # 現在時刻
            now = BJTime.get_time_now()

            # 移動前の可視領域減算
            if not hexgrid_controller.update_visible_area(visibility = player["visibility"],
                                                          division_id = division["division_id"],
                                                          switch=False):
                raise Exception("可視領域減算に失敗")

            # 移動(部隊)
            if not division_controller.move_division(self._division_id, self._dest_col, self._dest_row):
                self._logger.error("部隊の移動に失敗")
                raise Exception("部隊の移動に失敗")

            # 移動(プレイヤー)
            if not player_controller.move_user(self._user_id, self._dest_col, self._dest_row):
                self._logger.error("プレイヤーの移動に失敗")
                raise Exception("プレイヤーの移動に失敗")

            # 移動後の可視領域可算
            if not hexgrid_controller.update_visible_area(visibility=player["visibility"],
                                                          division_id = division["division_id"],
                                                          switch = True):
                logging.error("移動後の可視領域可算に失敗")
                raise Exception("移動後の可視領域可算に失敗")


            # 可視範囲を共有する通信中のプレイヤー(移動するプレイヤーも含む）にプレイヤーの移動を通知
            notify_move_player.notify_update_hexgrid(moving_player_info, player["visibility"], now)

        except DBError as e:
            logging.error("EventMove::run: caught DBError: " + e.message)

        except Exception as e:

            # 状態を初期化しておく
            player_controller.update_user_status("ready")
            division_controller.update_division_status("ready")

            logging.error(e)

            # プレイヤーにエラーを通知
            message = "行軍キャンセル : "
            payload = { "event" : "error",
                        "data" : { "message" : message}}
            BJSocketHandler.send_player(self._user_id, payload)

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
            self._dest_col = data[1]
            self._dest_row = data[2]

            return True

        except Exception as e:
            self._logger.error(u"不正な形式のレコード", e.message, self._event_record)
            return False

        assert False

    @classmethod
    def create_recode(cls, user_id, division_id, dest_col, dest_row, datetime):
        """
        レコード作成
        :param user_id: 移動するユーザー
        :param division_id: 移動する部隊
        :param dest_col: 目的地col
        :param dest_row: 目的地row
        :param datetime: 到着時刻
        :return: event_record[event_id, ...]
        """

        # データ部
        # "division_id,col,row"
        data = str(division_id) + "," + str(dest_col) + "," + str(dest_row)

        event = event_controller.create_event(datetime=datetime,
                                              object=user_id,
                                              subject="none",
                                              event_name="move",
                                              data=data)

        return event

if __name__ == "__main__":

    date = BJTime.get_time_now()
    print(date)
    e = EventMove.create_recode(user_id="u_id",
                            division_id="div_id",
                            dest_col="1",
                            dest_row="2",
                            datetime=date)
    print(e)