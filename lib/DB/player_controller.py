from logging import getLogger, StreamHandler, DEBUG
import sys
from lib.DB.DBSingleton import *
from lib.util import BJTime

def get_players_by_visibility(visibility, isVisible, hexes = None):
    """
    可視権から可視範囲上のプレイヤー情報を取得
    :param visibility: 可視権
    :param isVisible: true ? 可視なプレイヤー : 不可視なプレイヤー
    :param [hexes]: 指定されたグリッド [ [col, row, ...], ... ]
    :return: [{user_name, col, row, icon_id, country_id}]
    """

    print("on get_players_by_visibility")
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    results = None
    try:
        db = DBSingleton()

        where = "where hex_grid." + visibility
        if isVisible:
            where += " > 0 "
        else:
            where += " = 0 "
        # ヘックスが指定されていれば条件追加
        print("hexes = ", hexes)
        if hexes is not None:
            print(hexes)
            where += "and ("
            for hex in hexes:
                print("hex = ", hex[0], hex[1])
                where = where + " (hex_grid.col=" + str(hex[0]) + " and hex_grid.row=" + str(hex[1]) + ") or"
            where = where[:-3]
            where += ");"

        query  = "select user_name, user.col, user.row, icon_id, user.country_id from user " \
                "inner join hex_grid "\
                "on user.col=hex_grid.col and user.row=hex_grid.row " \
                + where
        results = db.exec(query, True)

    except DBError as e:
        logging.error(" message = " + e.message)
        return False

    result = []
    for player in results:
        record = {"user_name" : player[0],
                  "col" : player[1],
                  "row" : player[2],
                  "icon_id" : player[3],
                  "country_id" : player[4]}
        result.append(record)
    return result


def get_playerinfo_by_id(user_id):
    """
    ユーザーIDからプレイヤーの全情報を取得
    :param user_id:
    :return: dict[info_name, ...]
    """

    result = None
    try:
        db = DBSingleton()
        result = db.select("user_name",
                           "user_pass",
                           "user_id",
                           "col",
                           "row",
                           "country_id",
                           "icon_id",
                           "division_id", # 配下の部隊ID
                           "status", # 現在の状態
                            table="user", where="user_id = \"" + str(user_id) + "\"")

        # TODO : 可視権が国番号のみ
        result[0]["visibility"] = "visibility_" + str(result[0]["country_id"])

    except DBError as e:
        logging.error(e.message)
        raise Exception(u"DBエラー: ユーザー名取得失敗")

    if len(result) == 0:
        logging.error("There's no such a player in DB: user_id = " + str(user_id))
        raise Exception(u"user_idが" + str(user_id) + u"のプレイヤーは存在しない")
        return

    return result[0]


def get_userid_by_username(user_name):
    """
    ユーザー名からユーザーＩＤを取得
    該当のユーザー
    :param user_name:
    :return: ユーザーID
    """
    result = None
    try:
        db = DBSingleton()
        result = db.select("user_id",
                            table="user", where="user_name = \"" + str(user_name) + "\"")

    except DBError as e:
        logging.error(e.message)
        raise Exception("DBエラー:ユーザー名取得失敗")
        return False

    if len(result) == 0:
        logging.error("There's no such a player in DB: user_name = " + str(user_name))
        raise Exception(u"user_nameが" + str(user_name) + u"のプレイヤーは存在しない")
        return False

    return result[0]["user_id"]


def update_user_before_move(user_id, wait_untill):
    """
    移動に伴うユーザー情報の更新
    :param user_id:
    :param wait_untill: 到着予定時刻を表す時刻オブジェクト
    :param status: 移動中の状態
    :return: 更新成功 ?  : Exception
    """

    try:
        db = DBSingleton()
        query = "update user set"  + \
                " wait_untill = \"" +  BJTime.encode_to_sql(wait_untill)+ "\"" \
                " where user_id = \"" + str(user_id) + "\"";
        result = db.exec(query)

    except DBError as e:
        logging.error(e.message)
        raise Exception("DBエラー : 移動前のユーザー情報更新失敗")


def update_user_status(user_id, status):
    """
    プレイヤーのステータスを変更
    :param user_id:
    :param status:新しいステータス
    :return: 成功 ? True : False
    """
    if len(status) == 0:
        logging.error(u"statusが空")
        return False

    try:
        db = DBSingleton()
        query = "update user set"  + \
                " status = \"" + str(status) + "\"" \
                " where user_id= \"" + str(user_id) + "\""
        db.exec(query)
        return True

    except DBError as e:
        return False


def move_user(user_id, dest_col, dest_row):
        """
        プレイヤーを移動させる
        :param user_id: ユーザーID
        :param dest_col: 目的地col
        :param dest_row: 目的地row
        :return: 成功 ? True : False
        """

        try:
            db = DBSingleton()
            query = "update user set col=" + dest_col + ", row=" + dest_row
            where = " where user_id = \"" + user_id + "\""
            db.exec(query + where, False)
            return True

        except DBError as e:
            logging.error(e.message)
            return False


# 単体テスト用
if __name__ == "__main__":
    user_id_test3  = "387a0a9f4a7b4cfa94d1ed00d9fa9ffc"
    user_id_test = "d29b8baba6fb4e72aa9af32c9cbacb2b"


