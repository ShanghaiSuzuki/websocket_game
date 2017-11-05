from lib.DB import player_controller, hexgrid_controller, division_controller
from lib.DB.event_controller import add_event
from lib.GameMain import GameMain
from lib.event.EventDomestic import EventDomestic
from lib.util import BJTime

def ask_domestic(_cls, _self, data):
    """内政可能なヘックスの問い合わせに対する応答"""

    payload = {"event" : "response_ask_domestic",
               "data" : {}}

    player_info = player_controller.get_playerinfo_by_id(_self.get_secure_cookie("user_id").decode('utf-8'))
    col = data["col"]
    row = data["row"]

    # 内政可能な半径か
    adjacent_area = hexgrid_controller.get_adjacent_area(player_info["col"], player_info["row"])
    if not (col == player_info["col"] and row == player_info["row"]) and not ({"col" : col, "row" : row} in adjacent_area):
        _cls.send_member_by_id(player_info["user_id"], {"event" : "cancel",
                                                                    "data" :{"title" : "内政キャンセル", "reason" : "内政可能な半径ではない"}})
        return

    # 現在のヘックスの状態
    target_hex = hexgrid_controller.get_hexinfo(col,row)

    if target_hex is None:
        _cls.send_member_by_id(player_info["user_id"], {"event" : "cancel","data" :{"title" : "内政キャンセル" , "reason" : "存在しないヘックス"}})
        return

    # 自国のヘックスか
    if not target_hex["country_id"] == player_info["country_id"]:
        _cls.send_member_by_id(player_info["user_id"], {"event" : "cancel",
                                                                    "data" :{"title" : "内政キャンセル" , "reason" : "自国のヘックスではない"}})
        return
    # TODO : プレイヤーのステータスなどによる処理
    # 内政後の予想結果と
    gm = GameMain()
    food_result = target_hex["food"] + gm.get_affair().get_op_food_lv()
    money_result = target_hex["money"] + gm.get_affair().get_op_money_lv()
    required_time = gm.get_affair().get_op_domestic_speed()

    data = { "response" : True,
             "food_result" : int(food_result),
             "money_result" : int(money_result),
             "required_time" : int(required_time)}
    payload["data"] = data
    _cls.send_member_by_id(player_info["user_id"], payload)



def request_domestic(_cls, _self, data):
    """
    内政要求
    """
    payload = {"event" : "response_ask_domestic",
               "data" : {}}

    player_info = player_controller.get_playerinfo_by_id(_self.get_secure_cookie("user_id").decode('utf-8'))
    col = data["col"]
    row = data["row"]

    # プレイヤーは行動可能か
    if not player_info["status"] == "ready":
        _cls.send_member_by_id(player_info["user_id"], {"event" : "cancel",
                                                                    "data" :{"title" : "内政キャンセル", "reason" : "行動中"}})
        return

     # 内政可能な半径か
    adjacent_area = hexgrid_controller.get_adjacent_area(player_info["col"], player_info["row"])
    if not (col == player_info["col"] and row == player_info["row"]) and not ({"col" : col, "row" : row} in adjacent_area):
        _cls.send_member_by_id(player_info["user_id"], {"event" : "cancel",
                                                                    "data" :{"title" : "内政キャンセル", "reason" : "内政可能な半径ではない"}})
        return

    # 現在のヘックスの状態
    target_hex = hexgrid_controller.get_hexinfo(col,row)
    if target_hex == None:
         _cls.send_member_by_id(player_info["user_id"], {"event" : "cancel",
                                                                    "data" :{"title" : "内政キャンセル" , "reason" : "存在しないヘックス。"}})

    # イベント登録
    # TODO : プレイヤーのステータスなどによる処理
    gm = GameMain()
    finish_time = BJTime.add_time(BJTime.get_time_now(), gm.get_affair().get_op_domestic_speed())
    event = EventDomestic.create_recode(user_id=player_info["user_id"],
                                        division_id=player_info["division_id"],
                                        col=col,
                                        row=row,
                                        type=data["type"],
                                        datetime=finish_time)
    add_event(event)

    # プレイヤーと部隊の状態を変更
    division_controller.update_division_status(player_info["division_id"], "domestic")
    player_controller.update_user_status(player_info["user_id"], "domestic")

    # メインエンジンにイベントの実行時を通知
    gm = GameMain()
    gm.set_event_timestamp(finish_time)


