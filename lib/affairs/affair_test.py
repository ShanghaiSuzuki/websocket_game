from lib.affairs.affair_base import AffairBase

class AffairTest(AffairBase):
    """テスト情勢"""

    def __init__(self):
        super(AffairTest,self).__init__()

        self.settings = {"op_food_lv" : 1,
                         "op_money_lv" : 1,
                         "op_speed_lv" : 1000*60*0.1 #6秒
                         }

    def init(self):
        pass


