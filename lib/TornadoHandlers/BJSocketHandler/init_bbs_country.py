from lib.DB.DBSingleton import *


def init_bbs_country(_cls, _self, data):

    payload = { "event" : "init_bbs_country"}
    data = []

    #DBから会議室の内容を集める
    try:
        user_id = _self.get_secure_cookie("user_id").decode('utf-8')
        db = DBSingleton()
        country = db.select("country_id", table="user", where="user_id=" + "\""+str(user_id) + "\"")
        country = country[0]["country_id"]
        query = "select user.user_name, user.icon_id, bbs_country.date, bbs_country.article from user " \
                "inner join bbs_country "\
                "on user.user_id=bbs_country.user_id "\
                "where bbs_country.country_id = " + str(country) + \
                " order by bbs_country.date desc limit 20;"
        result = db.exec(query, True)

        for article in result:
            data.append({ "name" : article[0],
                          "icon" : article[1],
                          "date" : article[2].strftime("%Y-%m-%d %H:%M:%S"),
                          "article" : article[3]})


    except DBError as e:
        logging.error(u"init_bbs_country.py: 会議室の情報取得失敗。\nmessage = " + str(e))
        raise Exception("会議室の情報取得失敗")


    #送信するデータ組み立て
    payload["data"] = data
    _self.send_you(payload)

