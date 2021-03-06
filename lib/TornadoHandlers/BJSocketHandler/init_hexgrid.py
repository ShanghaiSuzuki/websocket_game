import logging

from lib.DB.DBSingleton import *
from lib.DB.player_controller import *
from lib.DB.hexgrid_controller import *


def init_hexgrid(_cls, _self, data):
    """
    クライアントのhex_gridへ初期化情報を送信する
    :param _cls: BJSocketHandlerのクラス
    :param _self: SocketHandlerのインスタンス
    :param data: 空
    :return:
    """

    payload = { "event": "init_hexgrid" }
    data = {}

    #DBから初期化情報を集める
    try:

        db = DBSingleton()

        # ヘックスグリッドの情報
        # TODO: map/map_*.pyからgame_statusのWHLを設定
        """
        result_whl = db.select("width", "height", "length", table="game_status")
        data["width"] = result_whl[0][0]
        data["height"] = result_whl[0][1]
        data["length"] = result_whl[0][2]
        """
        data["width"] = 1500
        data["height"] = 1500
        data["length"] = 50

        # プレイヤー情報（可視権含む）取得
        user_id = _self.get_secure_cookie("user_id").decode('utf-8')
        player= get_playerinfo_by_id(user_id)
        if not player:
            raise Exception("hex_grid上の自身のプレイヤー情報取得失敗")
        print("p0")
        # 可視範囲の全プレイヤー取得
        visible_players = get_players_by_visibility(player["visibility"], True)
        # 自身の情報をペイロードに格納
        data["player_self"] = {"name" : player["user_name"],
                                 "col" : player["col"],
                                 "row" : player["row"],
                                 "icon_id" : player["icon_id"],
                                 "country" : player["country_id"]}
        # 可視範囲の全プレイヤーの情報をペイロードに格納
        payload_players = []
        for visible_player in visible_players:
            payload_players.append({"col" : visible_player["col"],
                                    "row" : visible_player["row"],
                                    "icon_id" : visible_player["icon_id"],
                                    "country" : visible_player["country_id"]
                                    })

        data["new_players"] = payload_players

        # 領地の情報
        own_area = get_own_area(player["country_id"])
        data["own_area"] = []
        for hex in own_area:
            data["own_area"].append(hex)

        # 可視範囲のヘックスの情報
        visible_area = get_visible_area(player["visibility"])
        data["visible_area"] = []
        for hex in visible_area:
            data["visible_area"].append(hex)

        # 不可視領域のヘックスの情報
        unvisible_area = get_unvisible_area(player["visibility"])
        data["unvisible_area"] = []
        for hex in unvisible_area:
            data["unvisible_area"].append(hex)


    except Exception as e:
        logging.error(u"ヘックスグリッドの情報取得失敗。\n"
                      u"message = " + str(e))
        _self.send_error(u"ヘックスグリッドの情報取得失敗")
        return

    # 送信するデータ組み立て
    payload["data"] = data

    # 送信
    _self.send_you(payload)


