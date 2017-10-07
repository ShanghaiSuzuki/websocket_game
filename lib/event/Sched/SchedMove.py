from lib.event.Sched.SchedBase import SchedBase, schedulable


class SchedMove(SchedBase):

    def __init__(self, appointed_time, user_id, col, row, priority=0):
        SchedBase.__init__(self,user_id ,appointed_time,priority,col=col, row=row)
        self.kwargs["user_id"] = user_id

    def get_action(self):

        @schedulable(self.user_id)
        def move(user_id, col, row):
            """ 進軍する関数 """

            # 移動先で戦闘が発生する
            if _is_battle(user_id, col, row):
                from lib.event.EventBattle import EventBattle
                e = EventBattle(user_id, col, row)
            else:
                from lib.event.EventMove import EventMove
                e = EventMove(user_id, col, row)

            e.run()

        return move


def _is_battle(cls, user_id, col, row):
    return False
    """敵がいて戦闘が発生するか"""


