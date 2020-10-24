import pymysql
from ..config import Mysql_addr, Mysql_dbname_sotorrent, Mysql_password, Mysql_user


class DBPosts:
    db = pymysql.connect(Mysql_addr, Mysql_user, Mysql_password, Mysql_dbname_sotorrent)
    cursor = db.cursor()

    
    def statistic_concept_frequency_v0(self, concept_name : str, view_name : str = 'javaPosts'):
        concept_name_parameters = concept_name.strip().split('/')
        concept_name = concept_name_parameters[len(concept_name) - 1]
        sql = f"select COUNT(*) from `{view_name}` where `Body` like '%{concept_name}%'"
        ret = 0
        try:
            cursor.execute(sql)
            result = cursor.fetchone()[0]
            ret = result
        except:
            print("!!!error: sql execute fail")
        return ret
