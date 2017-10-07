"""
DBのterrianテーブル（地形情報）の操作
"""
from lib.DB.DBSingleton import DBError,DBSingleton
import logging


def get_terrian_info(terrian_type):
    """
    地形情報取得
    DBエラー、またはterrian_typeの地形がなければExceptionをスロー
    :param terrian_type:
    :return: {terrianの全てのキー}
    """

    result = None
    try:
        db = DBSingleton()
        result = db.select("terrian_type",
                           "availability", # 進入可能性
                           "infantry", # 歩兵移動補正
                           "heavy_inf", # 重歩兵移動補正
                           "cavalry", # 騎兵移動補正
                           "engineer", # 工兵移動補正
                          table="terrian", where="terrian_type \"" + str(terrian_type) + "\"")

    except DBError as e:
        logging.error(e.message)
        raise Exception("兵科の情報取得に失敗")
        return False

    if len(result) == 0:
        logging.error("Coudn't find terrian by terrian_type = " + str(terrian_type))
        raise Exception("terrian_typeが" + str(terrian_type) + "の地形がDBにない")
        return False

    return result[0]
if __name__ == "__main__":
    print(get_terrian_info("川"))
