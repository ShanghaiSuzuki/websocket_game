"""
時刻を表すオブジェクトの形式と処理をする
"""

# 時刻オブジェクトをエイリアスとしてt_timeに設定
from datetime import datetime as t_time
from datetime import timedelta as t_time_delta
format = "%Y-%m-%d %H:%M:%S"

def get_time_now():
    """
    現在の時刻オブジェクトを取得
    :return: t_time
    """
    return t_time.now()


def add_time(time, delta_millisecond):
    """
    時間を可算する
    :param time: get_time_now()で取得した形式の時刻
    :param delta: 増分（ミリ秒)
    :return:
    """

    return time + t_time_delta(milliseconds=delta_millisecond)


def encode_to_sql(time):
    """
    時刻オブジェクトをSQLのdatetimeを表す文字列に変換
    :param time: t_time型のオブジェクト
    :return: SQLのdatetimeを表す文字列
    """
    return time.strftime(format)


def decode_from_sql(timestamp):
    """
    SQLのtimestampをt_time型へ変換
    :param timestamp: SLQのdatetimeを表す文字列
    :return: t_time型のオブジェクト
    """
    return t_time.strptime(timestamp, format)
