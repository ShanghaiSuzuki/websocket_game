from lib.GameMain import GameMain


def schedulable(user_id):
    """実行後にスケジュールのリストから消去するデコレータ"""

    def _schedulable(func):

        def wrapper(*args, **kwargs):

            from lib.GameMain import GameMain
            gm = GameMain()
            print("SchedBase:size of sched = ", gm.get_size_sched())
            if args and kwargs:
                func(*args, *kwargs)
            elif args:
                func(*args)
            elif kwargs:
                func(**kwargs)
            else:
                func()


            gm.end_sched(user_id)
            print("SchedBase:size of sched = ", gm.get_size_sched())

        return wrapper

    return _schedulable


class SchedBase:
    """スケジューラーに登録されるスケジュールのベースクラス"""

    def __init__(self, user_id, appointed_time, priority=0, *args, **kwargs):
        self.user_id = user_id
        self.appointed_time = appointed_time
        self.priority = priority
        self.args = args
        self.kwargs = kwargs

    def get_action(self):
        """実行部分の関数を取得"""
        raise NotImplementedError()


