import pymysql
import pandas as pd
from ..config import Mysql_addr, Mysql_dbname_sotorrent, Mysql_password, Mysql_user, pre_generated_views_in_Mysql


class DBPosts:
    db = pymysql.connect(Mysql_addr, Mysql_user,
                         Mysql_password, Mysql_dbname_sotorrent)
    cursor = db.cursor()

    def statistic_concept_frequency_v0(self, concept_name: str, view_name: str = 'JavaPosts'):
        concept_name_parameters = concept_name.strip().split('/')
        concept_name = concept_name_parameters[len(concept_name) - 1]
        sql = f"select COUNT(*) from `{view_name}` where LOCATE('{concept_name}',`Body`)"
        ret = 0
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()[0]
            ret = result
        except:
            print("!!!error: sql execute fail")
        return ret

    def collect_posts_by_tag(self, tag_name: str):
        answer_cursor = self.db.cursor()
        if tag_name in pre_generated_views_in_Mysql.keys():
            sql = f"select `Id`, `Body`, `Tags`, `Title`, `Score`, `ViewCount`, `FavoriteCount`, `AcceptedAnswerId` from `Posts` where LOCATE('<java>', `Tags`) <> 0"
        else:
            # 有些tag相关的帖子已经事先生成了view，写在config里
            java_view_name = pre_generated_views_in_Mysql[tag_name]
            sql = f"select `Id`, `Body`, `Tags`, `Title`, `Score`, `ViewCount`, `FavoriteCount`, `AcceptedAnswerId` from `{java_view_name}`"
        try:
            self.cursor.execute(sql)
            while 1:
                row = self.cursor.fetchone()
                if row is None:
                    break
                if row[2] is None:
                    continue
                item = {
                    'Id': row[0],
                    'Body': row[1],
                    'Tags': row[2],
                    'Title': row[3],
                    'Score': row[4],
                    'ViewCount': row[5],
                    'FavoriteCount': row[6]
                }
                answer_sql = f"select `Id`, `Body`, `Score` from `Posts` where `ParentId` = {row[0]}"
                answer_cursor.execute(answer_sql)
                answers_rows = answer_cursor.fetchall()
                answers = [{
                    'Body': r[1],
                    'Score': r[2],
                    'Accepted': bool(r[0] == row[7])
                } for r in answers_rows]
                item['Answers'] = answers
                yield item
        except Exception as e:
            print(e)
