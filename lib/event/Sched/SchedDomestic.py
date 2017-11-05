
from lib.DB.DBSingleton import DBSingleton, DBError
from lib.TornadoHandlers.BJSocketHandler import BJSocketHandler
from lib.DB import event_controller, player_controller, hexgrid_controller, division_controller, country_controller
from lib import GameMain
from lib.util import BJTime
from lib.TornadoHandlers.BJSocketHandler.notify_move_player import notify_move_player
from lib.TornadoHandlers.BJSocketHandler import BJSocketHandler
import logging


class SchedEventDomestic():
    """
    定期的な内政イベント
    ゲームレベルの内政時間のインターバルごとに実行され、王都に国内の資源を回収する
    """


    def __init__(self, event_record):

        # レコード
        self._event_record = event_record

        # ロガー
        self._logger = logging.getLogger(__name__)

    def run(self):
        """
        :return: 成功 ? True : False
        """

        self._logger.debug("enter EventSchedDomestic run")
        self._logger.debug("event_record=", self._event_record)

        try:

            db = DBSingleton()

            # 可算前のの国情報取得
            ex_countries = country_controller.get_all_countryinfo()

            # 全ての国で食糧可算
            query = "UPDATE country" \
                    "   SET food = ((SELECT" \
                    "       SUM(hex_grid.food) from hex_grid" \
                    "       WHERE hex_grid.country_id = country.country_id" \
                    "       GROUP BY hex_grid.country_id) + country.food)" \
                    "WHERE EXISTS(SELECT 1 FROM hex_grid" \
                    "          WHERE hex_grid.country_id = country.country_id);"

            db.exec(query)

            # 全ての国で商業可算
            query = "UPDATE country" \
                    "   SET money = ((SELECT" \
                    "       SUM(hex_grid.money) from hex_grid" \
                    "       WHERE hex_grid.country_id = country.country_id" \
                    "       GROUP BY hex_grid.country_id) + country.money)" \
                    "WHERE EXISTS(SELECT 1 FROM hex_grid" \
                    "          WHERE hex_grid.country_id = country.country_id);"
            db.exec(query)

            print("SchedDomestic run")

            # イベントをインターバルでチェーン
            gm = GameMain.GameMain()
            next_time = BJTime.add_time(BJTime.get_time_now(), gm.get_affair().get_domestic_interval())
            next_event = SchedEventDomestic.create_recode(next_time)
            event_controller.add_event(next_event)
            gm.set_event_timestamp(next_time)

            # それぞれの国へ通知
            new_countries = country_controller.get_all_countryinfo()
            for i in range(0, len(new_countries)):
                message = "食糧 " + str(new_countries[i]["food"]) + " → " + str(ex_countries[i]["food"]) + "\n"
                message += "資金 " + str(new_countries[i]["money"]) + " → " + str(ex_countries[i]["money"])
                payload = {"event" : "notify",
                           "data" : {"title" : "徴税結果",
                                      "message" : message}}
                BJSocketHandler.BJSocketHandler.send_member_by_country(new_countries["country_id"], payload)


        except DBError as e:
            logging.error("EventMove::run: caught DBError: " + e.message)

        except Exception as e:
            logging.error(e)


    def _decode_recode(self):
        """
        デコードするデータなし
        :param event_record:
        :return: 常にTrue
        """
        return True

    @classmethod
    def create_recode(cls, datetime):
        """
        レコード作成
        :param datetime: 次の実行までのインターバル
        :return: event_record[event_id, ...]
        """

        # データ部
        # "division_id,col,row"

        event = event_controller.create_event(datetime=datetime,
                                              object="none",
                                              subject="none",
                                              event_name="sched_domestic",
                                              data="")

        return event