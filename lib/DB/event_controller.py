"""
DBのeventテーブルの操作
"""

from lib.DB.DBSingleton import DBSingleton, DBError
from lib.util import BJTime
import logging


def add_event(event_record):
    """
    イベントのレコードをDBへ追加
    :param event_record: イベントのレコード
    :return: 成功 ? True : False
    """

    try:
        db = DBSingleton()
        db.insert(table="event",
                  status=event_record["status"],
                  datetime=event_record["datetime"],
                  object=event_record["object"],
                  subject=event_record["subject"],
                  event_name=event_record["event_name"],
                  data=event_record["data"])

    except DBError as e:
        logging.error(e.message)
        return False

    return True


def create_event(datetime, object, subject, event_name, data, status="ready"):
    """
    イベントレコードを生成するヘルパー
    イベントレコードの形式を強要する
    :param datetime: 予定時間(必須)
    :param object:　主体
    :param subject:　対象
    :param event_name:　イベントの種類名(必須)
    :param data:　イベント用のデータ(str)
    :param status:　レコードの状態
    :return: 成功 ? event_record{datetime, ...} : None
    """

    event_record = { "datetime" : BJTime.encode_to_sql(datetime),
                     "object" : str(object),
                     "subject" : str(subject),
                     "event_name": str(event_name),
                     "data" : str(data),
                     "status" : str(status)}

    if datetime is None or event_name is None:
        logging.error(event_record)
        return None

    return event_record


def peek_event():
    """
    DBの中から最も早くスケジュールされた待機中のイベントを参照
    エラーの時はExceptionをスロー
    :return: 存在する？　EventRecord : None
    """

    try:
        db = DBSingleton()
        result = db.select("event_id",
                           "status",
                           "datetime",
                           "object",
                           "subject",
                           "event_name",
                           "data",
                           table="event",
                           where="datetime = (select min(datetime) from event where status = \"ready\")")

        # 待機中のイベントなし
        if len(result) == 0:
            return None

        # 待機中のイベントがある
        else:
            print(result[0])
            return result[0]

    except DBError as e:
        logging.error(e.message)
        raise Exception


def remove_event(event_id):
    """
    DBからイベントのレコードを削除
    :param event_id: イベントID
    :return: 成功 ? True : False
    """

    try:
        db = DBSingleton()
        db.delete(table="event", where="event_id=\"" + str(event_id) + "\"")

    except DBError as e:
        logging.error(e.message)
        return False

    return True


def peek_event_all():
    """
    DBに残っている全ての待機中イベントのレコードを参照（降順）
    :return:  存在する ? [EventRecord] : None
    """

    try:
        db = DBSingleton()
        query = "SELECT event_id, status, datetime, object, subject, event_name, data from event " \
                "WHERE status=\"ready\""
        result = db.exec(query, True)

        if len(result) == 0:
            return None
        else:
            return result

    except DBError as e:
        logging.error(e.message)
        raise Exception("DBエラー : 待機中のイベントのレコードの参照に失敗")

