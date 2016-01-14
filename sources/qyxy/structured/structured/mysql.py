# -*- coding: utf-8 -*-

import MySQLdb
import settings


class Mysql(object):
    """更新一个公司的数据到mysql数据库
    """
    def __init__(self):
        confs = settings.mysql_confs
        self.db = MySQLdb.connect(host=confs['host'],
                                  user=confs['user'],
                                  passwd=confs['passwd'],
                                  db=confs['db'],
                                  port=confs['port'])

        self.cursor = self.db.cursor()

    def update_tables(self, company_data={}):
        sqls = settings.sqls
        tables = settings.tables

        for table in tables:
            data = settings[table+"_data"]
            for key in data:
                if key in table:
                    data[key] = company_data[key]
            select_is_exist = sqls[table+"_select_is_exist"]
            select_id = sqls[table+"_select_id"]
            insert = sqls[table+"_insert"]
            update = sqls[table+"_update"]
            self.update_table(select_is_exist=select_is_exist,
                              select_id=select_id, insert=insert,
                              update=update, data=data)

        self.db.close()

    def update_table(self, select_is_exist="", select_id="",
                     insert="", update="", data={}):
        db = self.db
        cursor = self.cursor

        # check is the company's data exist, if exist update else insert
        cursor.execute(select_is_exist, data)
        results = cursor.fetchall()
        for row in results:
            data['id'] = row[0]

        if data['id'] == 0:
            # get the id from mysql
            cursor.execute(select_id, data)
            results = cursor.fetchall()
            for row in results:
                data['id'] = row[0] + 1
            if data['id'] == 0:
                data['id'] = 1
            cursor.execute(insert, data)
        else:
            cursor.execute(update, data)

        db.commit()
