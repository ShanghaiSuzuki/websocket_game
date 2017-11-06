import logging
from lib.TornadoHandlers.BJSocketHandler import BJSocketHandler
from lib.DB import hexgrid_controller
from lib.DB import player_controller


def notify_move_player(moving_player_info, visibility, time):
    """
    現在オンラインのプレイヤーに最新のヘックスグリッドの状態を可視権別に送信する
    :param moving_player_info: 移動するプレイヤーの移動前/後座標など
    :param visibility: 移動するプレイヤーの可視権
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
            data["visible_area"].append({ "col" : hex["col"], "row" : hex["row"], "type" : hex["type"]})

        # 新しい不可視領域のヘックスの情報
        unvisible_area = hexgrid_controller.get_unvisible_area(visibility,time)
        data["unvisible_area"] = []
        for hex in unvisible_area:
            data["unvisible_area"].append({ "col" : hex["col"], "row" : hex["row"], "type" : hex["type"]})

        # 新しい領地
        own_area = hexgrid_controller.get_own_area(moving_player_info["country_id"], time)
        data["own_area"] = [own_area[0]]

        # 移動したプレイヤーの情報
        data["moving_player"] = moving_player_info

        # 新しい可視領域に現れたプレイヤー
        data["new_players"] = player_controller.get_players_by_visibility(visibility, True, data["visible_area"])

        # 可視権を持つオンラインのプレイヤーに送信
        payload["data"] = data
        BJSocketHandler.BJSocketHandler.send_member_by_visibility(payload, visibility)


        # TODO: 他国
        # data["new_players"] = []
        # data["removed_players"] = []
        # for country:
            # data
        return True

    except Exception as e:

        logging.error(u"BJSocketHandler_init: ヘックスグリッドの情報取得失敗。\nmessage = " + e.message)

        return False

    assert False
