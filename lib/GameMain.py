# メインエンジン
# Singleton

import logging
import sched
import threading
import time

from lib.DB.DBSingleton import *
from lib.DB import event_controller
from lib.event.EventBase import EventBase
from lib.event.EventMove import EventMove
from lib.event.EventDomestic import EventDomestic
from lib.event.Sched import SchedDomestic
from lib.util import detailed_error
from lib.util import BJTime
from lib.affairs.affair_test import AffairTest
from lib.maps.map_test import MapTest
from threading import Condition
from threading import Lock


class SchedError(Exception):
    u"""スケジュールされたイベントから送出する例外"""

    def __init__(self, message):
        self.message = message


class GameMain:
    u"""メインエンジン（シングルトン)
        起動後はイベントループを内部に持ち、スケジュールされたイベントを処理する"""

    _instance = None

    _lock = Lock() # メインエンジンのロック
    _logger = None # メインエンジンロガー
    _dbname = None # データベースの名前
    _loop_lock = Condition() # イベントループの条件ロック
    _current_event_timestamp = None # 待機中のイベントの実行時間
    _game_settings = {} # ゲームの設定

    def __init__(self):
        pass

    def __new__(cls):

        with cls._lock:
            if cls._instance is None:
                cls._instance = object.__new__(cls)
                cls._queue = {}
                cls._scheduler = sched.scheduler(time.time, time.sleep)

                # logger設定
                cls._logger = logging.getLogger(__name__)
                cls._logger.debug("GameMain was created")

        return cls._instance

    @classmethod
    def run(cls):
        u"""ゲームのメインエンジンを起動する
            内部でイベントループを違うスレッドで起動させる"""

        db = DBSingleton()
        status = db.select("status", table="game_status")

        # TODO: 情勢実装
        affair = AffairTest()
        map = MapTest()
        cls._game_settings= {"affair": affair,
                             "map": map}



        print("status: ", status)
        if status[0]["status"] != "ongoing":
            cls.__start_new_year()

        # イベントループスレッド起動
        loop = threading.Thread(target=cls.loop, daemon=False)
        loop.start()

        cls._logger.info("Game system started running")

    @classmethod
    def loop(cls):
        u"""イベントループ
            スケジューラが空の時、スレッドはConditionでブロックされ、新しいスケジュールが追加されるまで待機する"""

        cls._logger.debug("loop() started")

        # イベントループ本体
        while True:

            time.sleep(0.1)

            # 待機中のイベントがなければスキップ
            if cls._current_event_timestamp is None:
                continue

            # 最速のイベントの実行時間が過ぎていれば実行
            if cls._current_event_timestamp <= BJTime.get_time_now():

                # 予定時間が一番早いイベントをDBから参照
                current_event_record = event_controller.peek_event()

                # 待機中のイベントがなければスキップ
                if current_event_record is None:
                    continue

                # イベントレコードを削除
                event_controller.remove_event(current_event_record["event_id"])

                # イベントディスパッチ処理
                event = None
                if current_event_record["event_name"] == "move":
                    event = EventMove(current_event_record)
                elif current_event_record["event_name"] == "domestic":
                    event = EventDomestic(current_event_record)
                elif current_event_record["event_name"] == "sched_domestic":
                    event = SchedDomestic.SchedEventDomestic(current_event_record)

                try:
                    event.run()
                except NotImplementedError:
                    cls._logger.error("実装されていないイベントが呼び出された", detailed_error.get_error())
                except Exception as e:
                    cls._logger.error(e, detailed_error.get_error())

                # 次に待機しているイベントがあれば予定時間をセット
                next_event_record = event_controller.peek_event()
                print("next_event_record=", next_event_record)
                if next_event_record is not None:
                    cls._current_event_timestamp = next_event_record["datetime"]
                else:
                    cls.set_event_timestamp(None)

        cls._logger.info("loop() ended")

    @classmethod
    def set_event_timestamp(cls,  event_timestamp):
        """
        待機中のイベントと新しいイベントの実行予定時間を比較し、更新する
        :param timestamp: 新しいイベントの実行予定時間
        :return:
        """

        with cls._lock:

            # 待機中のイベントがない場合Noneをセットする
            if event_timestamp is None:
                cls._current_event_timestamp = None
                return

            # メインエンジンに次のイベントの予定時刻がセットされていない場合
            if cls._current_event_timestamp is None:
                cls._current_event_timestamp = event_timestamp

            # メインエンジンにセットされているイベントの予定時刻よりも、新しいイベントの予定時刻が早い場合
            elif cls._current_event_timestamp > event_timestamp:
                cls._current_event_timestamp = event_timestamp

    @classmethod
    def __start_new_year(cls):
        u"""新年度をスタートさせる"""

        # 情勢読み込み
        cls._game_settings["affair"].init()

        # マップ作製
        cls._game_settings["map"].init()

        # TODO : この位置で開始させると他のイベントが入るまでcurrent_event_timeがNoneでループ回らない
        # 内政イベントチェーン開始
        from lib.event.Sched.SchedDomestic import SchedEventDomestic
        from lib.DB import event_controller
        next_time = BJTime.add_time(BJTime.get_time_now(), 1000*10)
        event = SchedEventDomestic.create_recode(next_time) # 10秒後に開始
        event_controller.add_event(event)
        GameMain.set_event_timestamp(next_time)

    @classmethod
    def get_affair(cls):
        """情勢を呼び出す"""

        return cls._game_settings["affair"]

    @classmethod
    def get_map(cls):
        """マップを呼び出す"""

        return cls._game_settings["map"]


if __name__ == "__main__":
    import sched, time
    import threading
    from threading import Condition, Lock

    s = sched.scheduler(time.time, time.sleep)

    def print_time(arg = "default"):
        print("p, time=", time.time(), " arg=", arg)

    condition = Condition()


