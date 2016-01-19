# -*- coding: utf-8 -*-

import json
import fileinput
import profiles.consts as consts
from clawer_parse import tools
from clawer_parse.models import (
    Basic,
    IndustryCommerceAdministrativePenalty,
    IndustryCommerceBranch,
    IndustryCommerceChange,
    IndustryCommerceCheck,
    IndustryCommerceClear,
    IndustryCommerceDetailGuarantee,
    IndustryCommerceException,
    IndustryCommerceIllegal,
    IndustryCommerceMainperson,
    IndustryCommerceMortgage,
    IndustryCommerceMortgageDetailChange,
    IndustryCommerceMortgageDetailGuarantee,
    IndustryCommerceMortgageGuaranty,
    IndustryCommerceRevoke,
    IndustryCommerceShareholders,
    IndustryCommerceSharepledge,
    IndustryMortgageDetailMortgagee,
)
from profiles.mappings import mappings


class Parse(object):
    """解析爬虫生成的json结构
    """

    mappings = mappings

    def __init__(self, clawer_file_path=''):
        self.keys = consts.keys
        if (clawer_file_path == ''):
            raise Exception('Must give clawer json file path.')

        else:
            self.companies = {}
            for line in fileinput.input(clawer_file_path):
                company = json.loads(line)
                for key in company:
                    self.companies[key] = company[key]

    def parse_companies(self):
        handled_num = 0
        for enter_id in self.companies:
            company = self.companies[enter_id]
            print u"\n公司注册Id: %s" % enter_id
            self.parse_company(company, enter_id)
            handled_num = handled_num + 1
        print u"\n=== 共导入%d个公司的数据 ===" % handled_num

    def parse_company(self, company={}, enter_id=0):
        keys = self.keys

        self.company_result = {'enter_id': enter_id}

        for key in company:
            if type(company[key]) == dict:
                if key in keys and key in mappings:
                    self.parse_dict(company[key], mappings[key])
            elif type(company[key] == list):
                if key in keys and key in mappings:
                    self.parse_list(key, company[key], mappings[key])

        if self.company_result.get('register_num') is None:
            self.company_result['register_num'] = enter_id

        self.conversion_type()
        self.write_to_mysql()
        self.company_result = {}

    def parse_dict(self, dict_in_company, mapping):
        for field in dict_in_company:
            if field in mapping:
                self.company_result[mapping[field]] = dict_in_company[field]

    def parse_list(self, key, list_in_company, mapping):
        pass

    def write_to_mysql(self):
        self.update(Basic)
        self.update(IndustryCommerceAdministrativePenalty)
        self.update(IndustryCommerceBranch)
        self.update(IndustryCommerceChange)
        self.update(IndustryCommerceCheck)
        self.update(IndustryCommerceClear)
        self.update(IndustryCommerceDetailGuarantee)
        self.update(IndustryCommerceException)
        self.update(IndustryCommerceIllegal)
        self.update(IndustryCommerceMainperson)
        self.update(IndustryCommerceMortgage)
        self.update(IndustryCommerceMortgageDetailChange)
        self.update(IndustryCommerceMortgageDetailGuarantee)
        self.update(IndustryCommerceMortgageGuaranty)
        self.update(IndustryCommerceRevoke)
        self.update(IndustryCommerceShareholders)
        self.update(IndustryCommerceSharepledge)
        self.update(IndustryMortgageDetailMortgagee)

    def update(self, model):
        company_result = self.company_result
        model().update_by_dict(model, company_result)

    def conversion_type(self):
        type_date = consts.type_date
        type_float = consts.type_float
        to_date = tools.trans_time
        to_float = tools.trans_float
        company_result = self.company_result

        for field in company_result:
            value = company_result[field]
            if field in type_date and value is not None:
                company_result[field] = to_date(value.encode('utf-8'))
            elif field in type_float and value is not None:
                company_result[field] = to_float(value.encode('utf-8'))
            elif type(value) == list:
                for d in company_result[field]:
                    for d_field in d:
                        d_value = d[d_field]
                        if d_field in type_date and d_value is not None:
                            d[d_field] = to_date(d_value.encode('utf-8'))
                        elif d_field in type_float and d_value is not None:
                            d[d_field] = to_float(d_value.encode('utf-8'))
