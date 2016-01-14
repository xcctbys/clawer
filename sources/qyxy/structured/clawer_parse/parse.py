# -*- coding: utf-8 -*-

import json
from mysql import Mysql


class Parse(object):
    """解析爬虫生成的json结构
    """
    def __init__(self, clawer_file_path='', mappings_file_path='', settings={}):
        self.keys = settings.keys
        self.mysql_confs = settings.mysql_confs
        if (clawer_file_path == '' or mappings_file_path == ''):
            raise Exception('must have clawer_file_path and mappings_file_path')

        else:
            with open(clawer_file_path) as clawer_file:
                self.companies = json.load(clawer_file)

            with open(mappings_file_path) as mappings_file:
                self.mappings = json.load(mappings_file)

    def handle_companies(self):
        for enter_id in self.companies:
            company = self.companies[enter_id]
            print u"\n公司注册Id: %s\n" % enter_id
            self.handle_company(company)

    def handle_company(self, company={}):
        mappings = self.mappings
        keys = self.keys
        self.company_result = {}
        for key in company:
            if type(company[key]) == dict:
                if key in keys and key in mappings:
                    self.handle_dict(company[key], mappings[key])
                else:
                    pass

            elif type(company[key] == list):
                if key in keys and key in mappings:
                    self.handle_list()
                else:
                    pass

            else:
                pass

        print self.company_result
        mycli = Mysql()
        mycli.update_table(self.company_result)

    def handle_dict(self, dict_in_company, mappings):
        for key in dict_in_company:
            if key != u"详情":
                self.company_result[mappings[key]] = dict_in_company[key]
            else:
                pass

    def handle_list(self):
        pass
