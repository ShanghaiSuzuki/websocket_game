from lib.DB.DBSingleton import DBSingleton, DBError
from lib.DB.player_controller import get_playerinfo_by_id, update_user_before_move, update_user_status
from lib.DB.branch_controller import get_branch_info
from lib.DB.hexgrid_controller import get_movable_area_by_division_id
from lib.DB.division_controller import get_division_info, update_division_before_move, update_division_status
from lib.util import BJTime
from lib.DB.event_controller import add_event
from lib.event.EventMove import EventMove
from lib.GameMain import GameMain
import logging

def move_query(_cls, _self, data):
    """進軍可能な進路を問い合わせに対する応答"""

    payload = {"event" : "move",
               "data" : {}}
    try:

        db = DBSingleton()
        user_id = _self.get_secure_cookie("user_id").decode('utf-8')

        # プレイヤーの状態
        player = get_playerinfo_by_id(user_id)

        # プレイヤーが待機中でないと移動できない
        if player["status"] != "ready":
            payload["data"] = {"response" : "deny",
                                "reason"   : u"行動中"}
            _self.send_you(payload)
            return False

        # 配下の師団がセットされていないと移動できない
        if not player["division_id"]:
            payload["data"] = {"response" : "deny",
                                "reason"   : u"配下の部隊がセットされていない"}
            _self.send_you(payload)
            return False

        # 配下の師団取得
        division = get_division_info(player["division_id"])

        # 師団の兵科情報取得
        branch = get_branch_info(division["branch_id"])

        # ゲームレベルから設定値を取得
        gm = GameMain()
        op_food_lv = gm.get_affair().get_op_food_lv()
        op_money_lv = gm.get_affair().get_op_money_lv()
        op_speed_lv = gm.get_affair().get_op_speed_lv()

        # 運用に必要な食糧と金 : 師団規模 * 兵科固定値 * ゲームレベル
        food_needed = division["quantity"] * branch["op_food"] * op_food_lv
        money_needed = division["quantity"] * branch["op_money"] * op_money_lv

        # 資金と食糧、それぞれ足りなければ移動不可
        if division["food"] < food_needed:
            payload["data"] = {"response" : "deny",
                                "reason"   : u"部隊の運用食糧が足りない。<br>" +
                                             u"部隊の保持食糧 : " + str(division["food"]) + "<br>" +
                                             u"必要な食糧 = 師団規模(" + str(division["quantity"]) +
                                            u")×兵科補正(" + str(branch["op_food"]) +
                                             u")×情勢補正(" + str(op_food_lv) + ") = " + str(food_needed)}
            _self.send_you(payload)
            return False

        elif division["money"] < money_needed:
            payload["data"] = {"response" : "deny",
                                "reason"   : u"部隊の運用資金が足りない。<br>" +
                                             u"部隊の保持資金 : " + str(division["money"]) + "<br>" +
                                             u"必要な資金 = 師団規模(" + str(division["quantity"]) +
                                            u")×兵科補正(" + str(branch["op_money"]) +
                                             u")×情勢補正(" + str(op_money_lv) + ") = " + str(money_needed)}
            _self.send_you(payload)
            return False


        # 移動可能なエリアと部隊の速度補正*地形補正を取得
        movable_area = get_movable_area_by_division_id(division["division_id"], player["col"], player["row"])

        # 補正にゲームレベルの進軍速度を掛ける
        for hex in movable_area:
            hex["time"] = hex["time"] * op_speed_lv

        payload["data"]["movables"] = movable_area
        payload["data"]["response"] = "move_query_accept"
        payload["data"]["food"] = food_needed
        payload["data"]["money"] = money_needed
        _self.send_you(payload)
        return True

    except DBError as e:
        logging.error(u"move_query失敗")
        _cls.send("error", "DBエラー : 進軍可能な範囲の問い合わせに失敗")

    except Exception as e:
        logging.error(e)
        payload["data"] = {"response" : "deny",
                            "reason"   : "サーバーエラー"}
        _self.send_you(payload)
        return False

    assert False


def move_request(_cls, _self, data):
    """
    行軍イベントをセットする
    :param _cls: BJSocketHandlerのクラス
    :param _self: BJSocketHandlerのインスタンス
    :param data: クライアントから受信したデータ
    :return:
    """

    user_id = _self.get_secure_cookie("user_id").decode('utf-8')
    payload = {"event" : "move" ,
               "data"  : {}}

    # 目的地
    dest_col = data["destination"][0]
    dest_row = data["destination"][1]

    try:

        """
        move_queryの焼き増しな部分があるが、queryとrequestの時間差または不正防止のため
        再度移動可能かどうか調べる
        """

        # プレイヤーの状態
        user_id = _self.get_secure_cookie("user_id").decode('utf-8')
        player = get_playerinfo_by_id(user_id)

        # プレイヤーが待機中でないと移動できない
        if player["status"] != "ready":

            payload["data"] = {"response" : "deny",
                                "reason"   : u"行動中"}
            _self.send_you(payload)
            return

        # 配下の部隊の状態
        division = get_division_info(player["division_id"])

        # 部隊がセットされていないと移動できない
        if not division:
            payload["data"] = {"response" : "deny",
                                "reason"   : u"配下の師団がセットされていない"}
            _self.send_you(payload)

        # 部隊の移動半径内でないと移動できない
        movable_area = get_movable_area_by_division_id(division["division_id"], player["col"], player["row"])

        required_time = False # 所要時間
        for hex in movable_area:
            if hex["col"] == dest_col and hex["row"] == dest_row:
                required_time = hex["time"]

        if not required_time:
            payload["data"] = {"response" : "deny",
                               "reason"   :  u"[" + str(dest_col) + u"," + str(dest_row) + u"]は移動可能半径外"}
            _self.send_you(payload)

        # 師団の兵科情報取得
        branch = get_branch_info(division["branch_id"])

        # ゲームレベルから設定値を取得
        gm = GameMain()
        op_food_lv = gm.get_affair().get_op_food_lv()
        op_money_lv = gm.get_affair().get_op_money_lv()
        op_speed_lv = gm.get_affair().get_op_speed_lv()

        # 運用に必要な食糧と金 : 師団規模 * 兵科固定値 * ゲームレベル
        food_needed = division["quantity"] * branch["op_food"] * op_food_lv
        money_needed = division["quantity"] * branch["op_money"] * op_money_lv

        # 資金と食糧、それぞれ足りなければ移動不可
        if division["food"] < food_needed:
            payload["data"] = {"response" : "deny",
                                "reason"   : u"部隊の運用食糧が足りない。<br>" +
                                             u"部隊の保持食糧 : " + str(division["food"]) + "<br>" +
                                             u"必要な食糧 = 師団規模(" + division["quantity"] +
                                            u")×兵科補正(" + str(branch["op_food"]) +
                                             u")×情勢補正(" + str(op_food_lv) + ") = " + str(food_needed)}
            _self.send_you(payload)
            return False

        elif division["money"] < money_needed:
            payload["data"] = {"response" : "deny",
                                "reason"   : u"部隊の運用資金が足りない。<br>" +
                                             u"部隊の保持資金 : " + str(division["money"]) + "<br>" +
                                             u"必要な資金 = 師団規模(" + division["quantity"] +
                                            u")×兵科補正(" + str(branch["op_money"]) +
                                             u")×情勢補正(" + str(op_money_lv) + ") = " + str(money_needed)}
            _self.send_you(payload)
            return False

        """
       チェックが終わったのでプレイヤー情報等を更新し、行軍イベントをセットする
        """

        # 到着予定時刻計算
        required_time = required_time * op_speed_lv # ゲームレベル適用
        current_time = BJTime.get_time_now()
        arrival_time = BJTime.add_time(current_time, required_time)

        # TODO: チェックと次の処理の間に状態が変更される可能性がある

        # 行軍のイベントレコードを作成
        event_record = EventMove.create_recode(user_id=player["user_id"],
                                               division_id=division["division_id"],
                                               dest_col=dest_col,
                                               dest_row=dest_row,
                                               datetime=arrival_time)
        # レコードの作成に失敗していれば失敗
        if event_record is None:
             payload["data"] = {"response" : "deny",
                                "reason"   : "イベントレコードの作成に失敗した。管理者に連絡して下さい。"}
             _self.send_you(payload)
             return

        # レコードをDBに登録
        add_event(event_record)

        # メインエンジンにイベントの実行時を通知
        gm = GameMain()
        gm.set_event_timestamp(arrival_time)

        # プレイヤーの状態を更新
        update_user_before_move(user_id=player["user_id"],
                                wait_untill=arrival_time)
        update_user_status(player["user_id"],"moving")

        # 部隊の状態を更新
        update_division_before_move(division_id=division["division_id"],
                                    food=food_needed,
                                    money=money_needed)
        update_division_status(division["division_id"], "moving")

        # クライアントに通知
        payload = {"event" : "move",
                   "data" : { "response" : "approval",
                               "arrival_time" : arrival_time.strftime("%Y-%m-%d %H:%M:%S")}}

        _self.send_you(payload)
        return

    except Exception as e:
        logging.error(e)
        _self.send_you({"error" : "エラーによりキャンセルされた。" + e.message})
        return

    assert False

if __name__ == "__main__":

    print("")


