import logging
from lib.TornadoHandlers.BJSocketHandler import BJSocketHandler
from lib.DB import hexgrid_controller
from lib.DB import player_controller


def notify_update_hexgrid(visibility, time):
    """
    現在オンラインのプレイヤーに最新のヘックスグリッドの状態を可視権別に送信する
    :param visibility: 可視権
    :param time: このタイムスタンプ以降に更新されたヘックスのみ適用
    :return: 成功　？　True : False
    """

    payload = { "event": "update_hexgrid" }
    data = {}

    try:



        # 新しい可視範囲のヘックスの情報
        visible_area = hexgrid_controller.get_visible_area(visibility, time)
        data["visible_area"] = []
        for hex in visible_area:
            data["visible_area"].append([hex["col"], hex["row"], hex["type"]])

        # 新しい不可視領域のヘックスの情報
        unvisible_area = hexgrid_controller.get_unvisible_area(visibility,time)
        data["unvisible_area"] = []
        for hex in unvisible_area:
            data["unvisible_area"].append([hex["col"], hex["row"], hex["type"]])

        # TODO:
        # 可視範囲の全プレイヤーの情報
        visible_players = player_controller.get_players_by_visibility(visibility, True, data["visible_area"])
        payload_players = []
        for player in visible_players:
            payload_players.append([player["user_name"],
                                    player["col"],
                                    player["row"],
                                    player["icon_id"],
                                    player["country_id"]])
        data["players"] = payload_players
        payload["data"] = data

        # 可視権を持つオンラインのプレイヤーに送信
        BJSocketHandler.BJSocketHandler.send_member_by_visibility(payload, visibility)

        return True

    except Exception as e:

        logging.error(u"BJSocketHandler_init: ヘックスグリッドの情報取得失敗。\nmessage = " + e.message)

        return False

    assert False