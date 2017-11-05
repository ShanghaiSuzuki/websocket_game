#情勢のベースクラス

class AffairBase:

    def __init__(self):

        # 設定
        self.settings = {"op_food_lv" : 1, # 進軍で消費する食糧
                         "op_money_lv" : 1, # 進軍で消費する資金
                         "domestic_interval" : 1000 * 60 * 0.5, # 内政感覚時間
                         "op_domestic_speed" : 1000 * 60 * 0.5,  # 内政消費時間
                         "op_move_speed_lv" : 1000 * 60 * 10 # １マスの進軍速度。10分
                         }


    #情勢の初期化（マップ読み込みやプレイヤーの配置、国設定など）を行う
    def init(self):
        raise NotImplementedError()

    #特殊な条件が発生するイベントをリスナーに加える
    def register_end_events(self, addEventListner):
        raise NotImplementedError()

    #終了条件

    #仕様可能なアイテム等の登録

    def get_op_food_lv(self):
        return self.settings["op_food_lv"]

    def get_op_money_lv(self):
        return self.settings["op_money_lv"]

    def get_op_speed_lv(self):
        return self.settings["op_move_speed_lv"]

    def get_op_domestic_speed(self):
        return self.settings["op_domestic_speed"]

    def get_domestic_interval(self):
        return self.settings["domestic_interval"]
