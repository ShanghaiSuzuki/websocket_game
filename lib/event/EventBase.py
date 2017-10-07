import logging


class EventBase():
    """
    イベントクラスの抽象クラス
    """
    def __init__(self, event_record):
        self._event_record = event_record
        self._logger = logging.getLogger(__name__)

    def run(self):
        """
        イベントの実行
        予定時刻になるとメインエンジンから呼ばれる
        イベントレコードをデコードし、それを元にイベントを実行する
        :return: NotImplementedError
        """

        return NotImplementedError("イベントが実装されていない")
