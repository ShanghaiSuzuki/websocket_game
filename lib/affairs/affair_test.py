from lib.affairs.affair_base import AffairBase

class AffairTest(AffairBase):
    """テスト情勢"""

    def __init__(self):
        super(AffairTest,self).__init__()

        self.settings = {"op_food_lv" : 1,
                         "op_money_lv" : 1,
                         "op_move_speed_lv" : 1000*60*0.1, # 6秒
                         "op_domestic_speed" : 1000 * 60 * 0.2, # 12秒
                         "domestic_interval" : 1000*60*0.1# 1０分
                         }

    def init(self):
        pass


