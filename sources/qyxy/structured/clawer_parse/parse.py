# -*- coding: utf-8 -*-

import json
from profiles.mappings import mappings
import profiles.settings as settings


class Parse(object):
    """解析爬虫生成的json结构
    """

    mappings = mappings

    def __init__(self, clawer_file_path=''):
        self.keys = settings.keys
        if (clawer_file_path == ''):
            raise Exception('must have clawer_file_path and mappings_file_path')

        else:
            with open(clawer_file_path) as clawer_file:
                self.companies = json.load(clawer_file)

    def handle_companies(self):
        for enter_id in self.companies:
            company = self.companies[enter_id]
            print u"\n公司注册Id: %s\n" % enter_id
            self.handle_company(company)

    def handle_company(self, company={}):
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

        # write to mysql
        print self.company_result

    def handle_dict(self, dict_in_company, mapping):
        for key in dict_in_company:
            if key != u"详情":
                self.company_result[mapping[key]] = dict_in_company[key]
            else:
                pass

    def handle_list(self):
        pass
