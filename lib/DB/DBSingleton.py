# データベースにアクセスするシングルトン
# スレッドセーフ
# TODO: SQL文を一行ずつ実行している。最適化したければ大量のクエリを一つのトランザクションで捌く関数を実装

from threading import Lock
import settings
import configparser
import logging
import pymysql

class DBError(Exception):
    """DBへの操作が失敗した場合に投げられる例外"""
    def __init__(self, message):
        self.message = "DBError: " + str(message)

# MySQLのDBを操作するシングルトン
class DBSingleton(object):

    _instance = None
    _lock = Lock()

    _logger = None
    _dbname = None

    def __init__(self):
        pass

    def __new__(cls):

        with cls._lock:
            if cls._instance is None:
                cls._instance = object.__new__(cls)

                # logger設定
                cls._logger = logging.getLogger(__name__)
                cls._logger.debug("DBSingleton created")

                # 設定読み込み
                config = configparser.ConfigParser()
                config.read(settings.__DBSINGLETON_CONF__)
                section = settings.__DBSINGLETON_SECTION__

                username = config.get(section, "username")
                userpass = config.get(section, "userpass")
                cls._dbname = config.get(section, "dbname")

                # mySQLのDBとコネクション作成
                cls._connector = pymysql.connect(host="localhost",
                                                 db=cls._dbname,
                                                 user=username,
                                                 passwd=userpass,
                                                 charset="utf8")

        return cls._instance

    # シングルトン破棄時に呼ぶ
    @classmethod
    def destroy(cls):
        cls._logger.debug("DBSingleton destroyed")
        with cls._lock:
            if cls._connector is not None:
                cls._connector.close()
                cls._connector = None
            if cls._instance is not None:
                cls._instance = None
            cls._dbname = None

    # SQL文発行
    # selectなどで値を返すの場合はresult=True
    # updateなどでテーブルを変更するものはresult=False
    # TODO: curはwith使う
    @classmethod
    def __exec(cls, query, result):

        with cls._lock:
            #cur =  cls._connector.cursor(OrderedDictCursor) if result == True else cls._connector.cursor()
            cur =  cls._connector.cursor()

            try:
                cur.execute(query)

            except pymysql.IntegrityError as err:
                cur.close()
                cls._logger.error("in __exec(): failed to execute " + query + "\nerr[0] = " + str(err.args[0]) + "\nerr[1] = " + str(err.args[1]))
                return False

            except pymysql.ProgrammingError as err:
                cur.close()
                cls._logger.error("in __exec(): failed to execute " + query + "\nerr[0] = " + str(err.args[0]) + "\nerr[1] = " + str(err.args[1]))
                return False

            except pymysql.InternalError as err:
                cur.close()
                cls._logger.error("in __exec(): failed to execute " + query + "\nerr[0] = " + str(err.args[0]) + "\nerr[1] = " + str(err.args[1]))
                return False

            if result == True:
                cls._connector.commit()
                ret = cur.fetchall()
                cur.close()
                return ret
            else:
                cls._connector.commit()
                cur.close()
                return True

    # INSERT文発行
    @classmethod
    def insert(cls, table, **kwargs):

        keys = table + "("
        values = "VALUES("

        for key, value in kwargs.items():

            # キー
            keys += key + ", "

            # 値
            if isinstance(value, str):
                value = "\"" + value + "\""
                values += value + ", "
            else:
                values += str(value) + ", "

        # 最後のカンマと空白を取り除く
        keys = keys[:-2]
        values = values[:-2]

        # 発行
        query = "INSERT " + keys + ") " + values + ");"
        if not cls.__exec(query, False):
            cls._logger.error("in insert(): failed to execute query")
            raise DBError(u"INSERT:失敗")


    # TODO: WHERE句以外は未実装
    @classmethod
    def select(cls, *args, **kwargs):
        """
        SELECT文発行
        :param args: keywards
        :param kwargs: table, [where]
        :return: list[dict, ...]
        """

        # keyが選択されていなければエラー
        if len(args) == 0:
            cls._logger.error(u"DBSingleton: select: キーが選択されていない")
            raise DBError(u"SELECT:キーが選択されていない")

        # tableが選択されていなければエラー
        if not "table" in kwargs:
            cls._logger.error(u"DBSingleton: select: テーブルが選択されていない")
            return DBError(u"SELECT:テーブルが選択されていない")

        # key回収
        keys = "" # select文
        keywards = [] # 戻り値のdictのkey
        for key in args:
            keywards.append(key)
            keys += key + ","

        # WHERE文があれば追加して発行
        # where文が空ならエラー
        # TODO: uppercaseでdictのkeyを変更する
        query = "SELECT " + keys[:-1] + " FROM " + cls._dbname + "." + kwargs["table"]
        if "WHERE" in kwargs:
            if len(kwargs["WHERE"]) == 0:
                cls._logger.error("recieved 0 length WHERE statement\nquery = " + query)
                raise DBError(u"SELECT:where句が空")
            query += " WHERE " + str(kwargs["WHERE"])
        elif "where" in kwargs:
            if len(kwargs["where"]) == 0:
                cls._logger.error("recieved 0 length WHERE statement\nquery = " + query)
                raise DBError(u"SELECT:where句が空")
            query += " WHERE " + str(kwargs["where"])

        query += ";"

        result = cls.__exec(query, True)
        if result == False:
            cls._logger.error("in select(): failed to execute query")
            raise DBError(u"SELECT:失敗")
            return

        ret = []
        for row in  result:

            i = 0
            result_dict = {}
            for col in row:
                result_dict[keywards[i]] = col
                i = i + 1

            ret.append(result_dict)

        return ret

    # UPDATE文発行
    # TODO: 一文で一つの項目しか変更できない。複数項目出来るようにする
    @classmethod
    def update(cls, **kwargs):

        query = "UPDATE "

        # テーブル
        if not "table" in kwargs or len(kwargs["table"]) == 0:
            cls._logger.error("in update() : table must be set")
            raise DBError(u"UPDATE:テーブルがセットされていない")

        query += cls._dbname + "." + str(kwargs["table"])

        # 対象のkey
        if not "key" in kwargs:
            cls._logger.error("in update() : key must be set")
            raise DBError(u"UPDATE:キーがセットされていない")

        query += " SET " + str(kwargs["key"])
        # 新しい値
        if not "value" in kwargs:
            cls._logger.error("in update() : value must be set")
            raise DBError(u"UPDATE:バリューがセットされていない")

        query += "=\"" + str(kwargs["value"]) + "\""

        # WHERE
        if not "where" in kwargs:
            cls._logger.error("in update() : where must be set")
            raise DBError(u"UPDATE:WHERE句がセットされていない")

        if len(kwargs["where"]) == 0:
            query += ";"
        else:
            query += " WHERE " + str(kwargs["where"]) + ";"

        #発行
        if not cls.__exec(query, False):
            cls._logger.error("in update(): failed to execute query")
            raise DBError(u"UPDATE:失敗")
        return True

    @classmethod
    def delete(cls, table, where):
        """
        DELETE文
        :param table: テーブル名
        :param where: WHERE句。空で全削除
        :return: 成功 ? : DBError
        """

        if len(str(where)) == 0 or where is None:
            query = "DELETE FROM " + cls._dbname + "." + str(table) + ";"
        else:
            query = "DELETE FROM " + cls._dbname + "." + str(table) + " WHERE " + str(where) + ";"

        cls._logger.debug("delete query = " + query)
        if not cls.__exec(query, False):
            cls._logger.error("in delete(): failed to execute query")
            raise DBError(u"DELETE文失敗")

    #直接SQL文を発行する
    #select文などで戻り値が必要な時はresult=True
    def exec(cls, query, result=False):
        """
        SQL文の実行
        失敗した時は
        :param query: 実行するSQL文
        :param result: Trueで実行結果を戻り値として得るスイッチ
        :return: result == True ? [[key, ...]] :
        """

        ret = cls.__exec(query, result)
        if not result:
            if ret is False:
                cls._logger.error("in exec(): failed to execute query")
                raise DBError(u"DELETE文失敗")
            return
        return ret

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    # ch = logging.FileHandler("test.log", mode="a")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    db = DBSingleton()
    result = db.select("user_name", table="user")
    print(result)

    """
    db.delete(table="users", where="id=3")
    allusers = db.select("*", table="users", where="id < 100")
    print(allusers)
    print(allusers[0][1])
    for user in allusers:
        print(user, flush=True)

    #db.insert(table="users", name="test4", id=10)
    #print(db.update(table="users", key = "name" , value="altered1", where = ""))
    """


    db.destroy()
