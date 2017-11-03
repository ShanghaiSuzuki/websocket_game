from lib.DB.DBSingleton import DBSingleton, DBError
from lib.DB.player_controller import get_players_by_visibility, get_userid_by_username, get_playerinfo_by_id
from lib.DB.branch_controller import get_branch_info
from lib.DB.hexgrid_controller import get_hexinfo
from lib.DB.country_controller import get_countryinfo_by_id
from lib.DB.division_controller import get_division_info_by_colrow, update_division_before_move, update_division_status
from lib.util import BJTime
from lib.DB.event_controller import add_event
from lib.event.EventMove import EventMove
from lib.GameMain import GameMain
import logging


def request_hexinfo(_cls, _self, _data):
    """ヘックスの情報を取得"""

    payload = {"event" : "response_hexinfo",
               "data" : {}}

    data = {"hex_info" : {}}

    # 取得しているプレイヤーの情報
    self_id = _self.get_secure_cookie("user_id").decode('utf-8')
    self_info= get_playerinfo_by_id(self_id)

    # ヘックスの情報
    hex_info = get_hexinfo(_data["col"], _data["row"])
    if hex_info == None:
        logging.error("failed to retrieve hex_info : " + str(data["col"]) + " , " + str(data["row"]))
        _cls.send_error(_self, "エラーでキャンセルされた")

    data["hex_info"]["type"] = hex_info["type"]
    if hex_info[self_info["visibility"]] > 0:
        # 可視範囲ならより詳細な情報取得
        data["hex_info"]["soldier"] = hex_info["soldier"]
        data["hex_info"]["food"] = hex_info["food"]
        data["hex_info"]["money"] = hex_info["money"]


    # 在中プレイヤーの情報
    other_player = get_players_by_visibility(self_info["visibility"], True, [{"col" : _data["col"], "row" : _data["row"]}])
    if len(other_player) != 0:

        # プレイヤー情報
        data["player_info"] = {}
        other_player = other_player[0]
        data["player_info"]["player_name"] = other_player["user_name"]
        country_id = other_player["country_id"]
        country_info = get_countryinfo_by_id(other_player["country_id"])
        data["player_info"]["country_name"] = country_info["country_name"]

    # 部隊情報
    division_info = get_division_info_by_colrow(_data["col"], _data["row"])
    if division_info:
        branch_info = get_branch_info(division_info["branch_id"])
        data["division_info"] = {}
        data["division_info"]["division_name"] = division_info["division_name"]
        data["division_info"]["status"] = division_info["status"]
        data["division_info"]["level"] = division_info["level"]
        data["division_info"]["quantity"] = division_info["quantity"]
        data["division_info"]["branch_name"] = branch_info["branch_name"]

    payload["data"] = data
    _self.send_you(payload)







