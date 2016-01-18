# -*- coding: utf-8 -*-

import json
import fileinput
import profiles.consts as consts
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
            raise Exception('must have clawer_file_path')

        else:
            self.companies = {}
            for line in fileinput.input(clawer_file_path):
                company = json.loads(line)
                for key in company:
                    self.companies[key] = company[key]

    def handle_companies(self):
        for enter_id in self.companies:
            company = self.companies[enter_id]
            print u"\n公司注册Id: %s\n" % enter_id
            self.handle_company(company, enter_id)

    def handle_company(self, company={}, enter_id=0):
        keys = self.keys
        self.company_result = {'enter_id': enter_id}
        for key in company:
            if type(company[key]) == dict:
                if key in keys and key in mappings:
                    self.handle_dict(company[key], mappings[key])
                else:
                    pass
            else:
                pass

        for key in company:
            if type(company[key] == list):
                if key in keys and key in mappings:
                    self.handle_list(key, company[key], mappings[key])
                else:
                    pass
            else:
                pass

        if self.company_result['register_num'] is None:
            self.company_result['register_num'] = enter_id
        self.write_to_mysql()
        self.company_result = {}

    def handle_dict(self, dict_in_company, mapping):
        for field in dict_in_company:
            if field != u"详情" and field != u"":
                self.company_result[mapping[field]] = dict_in_company[field]
            else:
                pass

    def handle_list(self, key, list_in_company, mapping):
        company_result = self.company_result
        if key == "ind_comm_pub_reg_shareholder":
            result = []
            for d in list_in_company:

                ind_shareholder = {}
                for field in d:
                    if type(d[field]) == str:
                        ind_shareholder[mapping[field]] = d[field]
                    if type(d[field]) == dict:
                        detail = d[field]
                        for detail_field in detail:
                            if detail_field in mapping:
                                ind_shareholder[mapping[detail_field]] = detail[detail_field]
                result.append(ind_shareholder)

            company_result["industry_commerce_shareholders"] = result

        else:
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
        model().update(model, company_result)
