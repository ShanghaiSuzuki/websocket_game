"""
DBのbranchテーブル(兵科)を操作
"""

import logging
from lib.DB.DBSingleton import DBSingleton, DBError

def get_branch_info(branch_id, where = None):
    """
    branch_idから兵科情報を取得
    :param branch_id: 兵科ID
    :return: {divisionの全てのキー}
    """

    result = None
    try:

        if where is None:
            where = "branch_id = \"" + str(branch_id) + "\""

        db = DBSingleton()
        result = db.select("branch_id",
                           "branch_name",
                           "atk",
                           "def",
                           "speed", # 進軍スピード
                           "visible_range", # 視界半径
                           "op_food", # 運用に必要な食糧
                           "op_money", # 運用に必要な資金
                           "draft_food", # 徴兵に必要な食糧
                           "draft_money", # 徴兵に必要な資金
                           "build", # 建築補正
                           "sabotage", # 破壊工作補正
                           "transportion", # 輸送補正
                           "infantry_atk", # 対歩兵攻撃補正
                           "infantry_def", # 対歩兵防御補正
                           "heavy_inf_atk", # 対重歩兵攻撃補正
                           "heavy_inf_def", # 対重兵防御補正
                           "cavalry_atk", # 対騎兵攻撃補正
                           "cavalry_def", # 対騎兵防御補正
                           "engineer_atk", # 対工兵攻撃補正
                           "engineer_def", # 対工兵防御補正
                           "liver", # 川移動補正
                           "plain", # 平地移動補正
                           "capital", # 首都移動補正
                           table="branch", where=where)

    except DBError as e:
        logging.error(e.message)
        raise Exception("兵科の情報取得に失敗")
        return False

    if len(result) == 0:
        logging.error("Coudn't find branch by branch_id = " + str(branch_id))
        raise Exception("branch_idが" + str(branch_id) + "の兵科がDBにない")
        return False

    return result[0]


def convert_branchid_to_name(branch_id):

    if branch_id == "infantry":
        return "歩兵"
    elif branch_id == "heavy_inf":
        return "重兵"
    elif branch_id == "cavalry":
        return "騎兵"
    else:
        return "不明"

if __name__ == "__main__":
    print(get_branch_info("infantry"))
