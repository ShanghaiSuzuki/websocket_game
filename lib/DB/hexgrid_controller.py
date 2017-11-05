"""
ヘックスグリッドの操作
"""
from lib.DB.DBSingleton import *
from lib.util import BJTime
from lib.util import detailed_error
import logging


def get_visible_area(visibility, timestamp=None):
    """
    可視権から可視範囲のグリッドを取得
    :param visibility: 可視権
    :param [timestamp]: オプション。この時刻オブジェクト以降に変更されたグリッドのみ取得する
    :return: list[dict[col, row, type]]
    """

    result = None
    try:

        # 可視権による条件
        where = str(visibility) + " > 0"

        # タイムスタンプによる条件
        if timestamp is not None:
            datetime = BJTime.encode_to_sql(timestamp)
            where += " and timestamp >= \"" + datetime + "\""

        db = DBSingleton()
        result = db.select("col", "row", "type",
                           table="hex_grid",
                           where=where)

    except DBError as e:
        logging.error(e.message)
        raise Exception("DBエラー : visibilityが" + str(visibility) + u"の可視範囲のグリッド取得失敗")
        return

    return result


def get_unvisible_area(visibility, timestamp=None):
    """
    可視権から不可視範囲のグリッドを取得
    :param visibility:
    :param [timestamp]: オプション。この時刻オブジェクト以降に変更されたグリッドのみ取得する
    :return: list[dict[col, row, type]]
    """
    result = None
    try:
        # 可視権による条件
        where = str(visibility) + " = 0"

        # タイムスタンプによる条件
        if timestamp is not None:
            datetime = BJTime.encode_to_sql(timestamp)
            where += " and timestamp >= \"" + datetime + "\""

        db = DBSingleton()
        result = db.select("col", "row", "type",
                           table="hex_grid",
                           where=where)
    except DBError as e:
        logging.error(e.message)
        raise Exception("DBエラー : visibilityが" + str(visibility) + u"の不可視範囲のグリッド取得失敗")
        return

    return result


def get_adjacent_area(col, row, _range = 1):
    """
    あるヘックスからレンジ内の隣接するヘックスを取得
    rangeが1より小さい時Exceptionをスロー
    :param col:
    :param row:
    :param range:
    :return: [ [col, row], ... ]
    """

    if _range < 1:
        logging.error("_range : " + str(_range) + " must be over 1")
        raise Exception("レンジの指定は1以上でなければならない。")
        return False

    # レンジ内の隣接するヘックス
    hexes = None
    where = ""
    for i in range(1, _range+1):
        for j in range(0, _range+1):
            where += " (col = " + str(col + j) + " and row = " + str(row - i + j) + ") or"
            where += " (col = " + str(col + i - j) + " and row = " + str(row + i) + ") or"
            where += " (col = " + str(col - i) + " and row = " + str(row - j) + ") or"
    where = where[:-3]

    # そのうちDBに実在するもの
    try:
        db = DBSingleton()
        hexex = db.select("col", "row", table="hex_grid", where=where)

    except DBError as e:
        logging.error(e.message)
        raise Exception("DBエラー")
        return False

    return hexex


def get_movable_area_by_division_id(division_id, col, row):
    """
    部隊IDから移動可能なエリアを取得
    DBエラー、または部隊IDの部隊がなければExceptionをスロー
    :param division_id:
    :param col: プレイヤーのcol
    :param row: プレイヤーのrow
    :return: [{col, row, time(速度補正)}]
    """

    result = None
    try:
        db = DBSingleton()

        # 部隊の兵科と座標
        from lib.DB.division_controller import get_division_info
        division = get_division_info(division_id)

        # 兵科の情報
        from lib.DB.branch_controller import get_branch_info
        branch = get_branch_info(division["branch_id"])


        # 隣接する座標を計算
        adjacent_area = get_adjacent_area(col, row, 1)

        # エリアの地形取得
        where = ""
        for hex in adjacent_area:
            where += " (col = " + str(hex["col"]) + " and row = " + str(hex["row"]) + ") or"
        where = where[:-3]
        terrian_type = db.select("col", "row", "type",
                           table="hex_grid", where=where)

        # 兵科速度 * 地形補正から所要時間を計算
        result = []
        for hex in terrian_type:
            result.append({"col" : hex["col"],
                           "row" : hex["row"],
                           "time" : branch["speed"] * branch[hex["type"]]})

    except DBError as e:
        logging.error(e.message)
        raise Exception("DBエラー")
        return False

    except Exception as e:
        raise e

    return result


def update_visible_area(visibility, division_id, switch):
    """
    部隊の視界内のヘックスの可視性を変更
    :param visibility: 可視権
    :param division_id: 部隊ID
    :param switch: True ? 可算 : 減算
    :return: 成功 ? True : False
    """

    try:

        # 部隊の情報
        from lib.DB.division_controller import get_division_info
        division = get_division_info(division_id)

        # 兵科の情報
        from lib.DB.branch_controller import get_branch_info
        branch = get_branch_info(division["branch_id"])

        # 現在の部隊の視界
        visible_area = get_adjacent_area(division["col"], division["row"], branch["visible_range"])
        visible_area.append({"col" : division["col"], "row" : division["row"]})

        # 更新
        if switch : switch = str("+")
        else : switch = str("-")

        where = "where "
        for hex in visible_area:
            where = where + "(col=" + str(hex["col"]) + " and row=" + str(hex["row"]) + ") or"
        where = where[:-3]

        query = "update hex_grid set " + \
                visibility + " = " + visibility + " " + switch + " 1 " + where
        db = DBSingleton()
        db.exec(query)

        print("update p6")
    except DBError as e:
        logging.error(e.message, detailed_error.get_error())
        return False

    except Exception as e:
        logging.error(e, detailed_error.get_error())
        return False

    return True


def get_hexinfo(col, row):
    """
    :param col: hex_gridのcol
    :param row: hex_gridのrow
    :return:
    """
    try:
        db = DBSingleton()
        result = db.select("col", "row",
                           "type",
                           "country_id",
                           "food",
                           "money",
                           "visibility_0",
                           "visibility_1",
                           table="hex_grid", where="col=" + str(col) + " and row = " + str(row))
        if len(result) == 0:
            return None
        else:
            return result[0]

    except DBError as e:
        logging.error(e.message, detailed_error.get_error())
        return None
    except Exception as e:
        logging.error(e, detailed_error.get_error())
        return None

def update_hex(col, row, **kargs):
    """
    ヘックスのレコードを更新
    :param col: 該当ヘックスcol
    :param row: 該当ヘックスrow
    :param kargs: {key : value, ...}
    :return: 成功 ? True : False
    """

    try:
        db = DBSingleton()

        sentence = "update hex_grid set"

        for key, value in kargs.items():
           sentence = sentence + " " + str(key) + " = \"" + str(value)  + "\""

        sentence += " where col = " + str(col) + " and row = " + str(row)

        db.exec(sentence)
        return True

    except DBError as e:
        logging.error(e.message, detailed_error.get_error())
        return False

# 単体テスト用
if __name__ == "__main__":

    #print(get_visible_area(2))
    print("***")
    #print(get_unvisible_area(2))
    print("***")
    #print("get_adjacent_area(2,8,1)")
    print(get_adjacent_area(5,4,1))
    print(get_movable_area_by_division_id(1))