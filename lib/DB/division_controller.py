"""
DBのdivisionテーブル（部隊）を操作
"""

from lib.DB.DBSingleton import *
import logging


def get_division_info(division_id):
    """
    部隊の情報を取得する
    DBエラーの時はDBErrorをスローする
    :param division_id: 部隊ID
    :return: 該当するIDの部隊 ? {divisionテーブルの全てのkey} : false
    """

    try:
        db = DBSingleton()
        result = db.select("division_id", # 部隊ID
                           "division_name", # 部隊名
                           "col", # 座標
                           "row", # 座標
                           "branch_id", # 兵科ID
                           "user_id", # 所有ユーザー
                           "country_id", # 所属国
                           "status", # 状態
                           "food", # 食糧
                           "money", # 資金
                           "level", # 練度
                           "quantity", # 規模
                           table="division", where="division_id = \"" + str(division_id) + "\"")

    except DBError as e:
        logging.error(e.message)
        raise Exception("部隊の情報取得に失敗")
        return False

    if len(result) == 0:
        return False

    return result[0]


def get_division_info_by_colrow(col, row):
    try:
        db = DBSingleton()
        result = db.select("division_id", # 部隊ID
                           "division_name", # 部隊名
                           "col", # 座標
                           "row", # 座標
                           "branch_id", # 兵科ID
                           "user_id", # 所有ユーザー
                           "country_id", # 所属国
                           "status", # 状態
                           "food", # 食糧
                           "money", # 資金
                           "level", # 練度
                           "quantity", # 規模
                           table="division", where="col="+str(col)+" and row="+str(row))

    except DBError as e:
        logging.error(e.message)
        raise Exception("部隊の情報取得に失敗")
        return False

    if len(result) == 0:
        return False

    return result[0]


def update_division_before_move(division_id, food, money, status="moving"):
    """
    移動に伴う部隊情報の更新
    :param division_id: 部隊ID
    :param food: 消費物資
    :param money: 消費資金
    :return: 更新成功 ? True : False
    """
    try:
        db = DBSingleton()
        query = "update division set"  + \
                " food = food - " + str(food) + \
                ", money =money-" + str(money) + \
                " where division_id = \"" + str(division_id) + "\"";
        db.exec(query)
        return True

    except DBError as e:
        logging.error(e.message)
        return False


def update_division_status(division_id, status):
    """
    部隊のステータスを変更
    :param division_id:
    :param status:新しいステータス
    :return: 成功 ? True : False
    """
    if len(status) == 0:
        logging.error(u"statusが空")
        return False

    try:
        db = DBSingleton()
        query = "update division set"  + \
                " status = \"" + str(status) + "\"" \
                " where division_id = \"" + str(division_id) + "\""
        db.exec(query)
        return True

    except DBError as e:
        return False


def move_division(division_id, dest_col, dest_row):
    """
    部隊を移動させる
    :param division_id: 部隊ID
    :param dest_col: 目的地col
    :param dest_row: 目的地row
    :return: 成功 ? True : False
    """

    try:
        db = DBSingleton()
        query = "update division set col="+dest_col+", row="+dest_row
        where = " where division_id = \"" + division_id + "\""
        db.exec(query + where, False)
        return True

    except DBError as e:
        logging.error(e.message)
        return False


def update_division(division_id, **kwargs):
    """
    部隊の情報更新
    :param division_id:
    :param kwargs:
    :return: 成功 ? True : False
    """
    try:
        db = DBSingleton()

        sentence = "update division set "
        for key, value in kwargs.items():
            sentence = sentence + key + " = \"" + str(value) + "\","
        sentence = sentence[:-1]
        sentence + " where division_id = \"" + str(division_id) + "\""
        db.exec(sentence)
        return True

    except DBError as e:
        return False
