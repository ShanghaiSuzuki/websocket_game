from lib.DB.DBSingleton import *
from logging import getLogger, StreamHandler, DEBUG

def get_countryinfo_by_id(country_id):

    try:

        db = DBSingleton()
        result = db.select("country_id",
                           "capital_col",
                           "capital_row",
                           "leader",
                           "country_name",
                           table="country", where="country_id = " + str(country_id))

        if len(result) == 0:
            return None

        return result[0]

    except DBError as e:
        logging.error(e.message);
        return None;

def get_all_countryinfo():
    """
    全ての国の情報を取得
    :return:
    """

    try:

        db = DBSingleton()
        result = db.select("country_id",
                           "capital_col",
                           "capital_row",
                           "leader",
                           "country_name",
                           table="country")

        if len(result) == 0:
            return None

        return result

    except DBError as e:
        logging.error(e.message);
        return None;
