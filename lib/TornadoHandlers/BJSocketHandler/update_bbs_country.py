import logging
from datetime import datetime as dt
from lib.DB.DBSingleton import *

def update_bbs_country(_cls, _self, data):

    payload = { "event" : "update_bbs_country"}
    send_data = None
    country = None

    try:

        #DBから最新の会議室への書き込みを取得
        user_id = _self.get_secure_cookie("user_id").decode('utf-8')
        db = DBSingleton()
        country = db.select("country_id", table="user", where="user_id=" + "\""+str(user_id) + "\"")
        country = country[0][0]
        query = "select user.user_name, user.icon_id, bbs_country.date, bbs_country.article from user " \
                "inner join bbs_country "\
                "on user.user_id=bbs_country.user_id "\
                "where bbs_country.country_id = " + str(country) + \
                " order by bbs_country.date desc limit 1;"
        result = db.exec(query, True)

        send_data= {"name" : result[0][0],
                "icon" : result[0][1],
                "date" : result[0][2].strftime("%Y-%m-%d %H:%M:%S"),
                "article" : result[0][3]}

    except DBError as e:
        logging.error(u"init_bbs_country.py: 会議室の情報取得失敗。\nmessage = " + e.message)
        raise Exception(u"会議室の情報取得失敗")

    #送信するデータ組み立て
    payload["data"] = send_data
    _cls.send_country(payload, country)


def write_bbs_country(_cls, _self, data):
    """会議室へ書き込み"""

    try:

        #DBへ書き込みを追加
        user_id = _self.get_secure_cookie("user_id").decode('utf-8')
        db = DBSingleton()
        country = db.select("country_id", table="user", where="user_id=" + "\""+str(user_id) + "\"")
        country = country[0][0]
        data = data.replace("\n", "<br>")
        db.insert(table="bbs_country",
                  user_id=str(user_id),
                  country_id=country,
                  article=str(data))

    except DBError as e:
        logging.error(u"init_bbs_country.write_bbs_country: 会議室への書き込み失敗。\nmessage = " + e.message)
        raise Exception(u"会議室への書き込み失敗")

    #更新を通知
    update_bbs_country(_cls, _self, {})


if __name__ == "__main__":

        db = DBSingleton()
        country = 0
        query = "select user.user_name, user.icon_id, bbs_country.date, bbs_country.article from user " \
                "inner join bbs_country "\
                "on user.user_id=bbs_country.user_id "\
                "where bbs_country.country_id = " + str(country) + \
                " order by bbs_country.date limit 20;"
        result = db.exec(query, True)

        print(result[0][2])
        print(result[0][2].strftime("%Y-%m-%d %H:%M:%S"))