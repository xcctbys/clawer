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
                    print "dict: ", key
                    self.parse_dict(company[key], mappings[key])
            elif type(company[key] == list):
                if key in keys and key in mappings:
                    print "list: ", key
                    self.parse_list(key, company[key], mappings[key])

        credit_code = self.company_result.get('credit_code')
        register_num = self.company_result.get('register_num')
        if credit_code is None:
            credit_code = register_num
        elif register_num is None:
            register_num = credit_code

        self.conversion_type()
        self.write_to_mysql()
        self.company_result = {}

    def parse_dict(self, dict_in_company, mapping):
        for field in dict_in_company:
            if field in mapping:
                self.company_result[mapping[field]] = dict_in_company[field]

    def parse_list(self, key, list_in_company, mapping):
        keys_to_tables = consts.keys_to_tables
        name = keys_to_tables.get(key)
        parse_func = self.key_to_parse_function(key)
        for d in list_in_company:
            value = parse_func(d, mapping)
            if name is not None and value is not None:
                self.company_result[name] = value

    def key_to_parse_function(self, key):
        keys_to_functions = {
            "ind_comm_pub_reg_shareholder": self.parse_ind_shareholder,
            "ind_comm_pub_reg_modify": self.parse_ind_modify,
            "ind_comm_pub_arch_key_persons": self.parse_ind_key_persons,
            "ind_comm_pub_arch_branch": self.parse_ind_branch,
            "ind_comm_pub_movable_property_reg": self.parse_ind_property_reg,
            "ind_comm_pub_equity_ownership_reg": self.parse_ind_ownership_reg,
            "ind_comm_pub_administration_sanction": self.parse_ind_sanction,
            "ind_comm_pub_business_exception": self.parse_ind_exception,
            "ind_comm_pub_serious_violate_law": self.parse_ind_violate_law,
            "ind_comm_pub_spot_check": self.parse_ind_check,

            "ent_pub_ent_annual_report": self.parse_ent_report,
            "ent_pub_shareholder_capital_contribution": self.parse_ent_contribution,
            "ent_pub_equity_change": self.parse_ent_change,
            "ent_pub_administration_license": self.parse_ent_license,
            "ent_pub_knowledge_property": self.parse_ent_property,
            "ent_pub_administration_sanction": self.parse_ent_sanction,

            "other_dept_pub_administration_license": self.parse_other_license,
            "other_dept_pub_administration_sanction": self.parse_other_sanction,

            "judical_assist_pub_equity_freeze": self.parse_judical_freeze,
            "judical_assist_pub_shareholder_modify": self.parse_judical_modify,
        }
        return keys_to_functions.get(key, lambda: "noting")

    def parse_ind_shareholder(self, dict_in_company, mapping):
        inner = {}
        for d in dict_in_company:
            d_map = mapping[d]
            inner[d_map] = dict_in_company[d]
        return inner    

    def parse_ind_modify(self, dict_in_company, mapping):
        pass

    def parse_ind_key_persons(self, dict_in_company, mapping):
        pass

    def parse_ind_branch(self, dict_in_company, mapping):
        pass

    def parse_ind_property_reg(self, dict_in_company, mapping):
        pass

    def parse_ind_ownership_reg(self, dict_in_company, mapping):
        pass

    def parse_ind_sanction(self, dict_in_company, mapping):
        pass

    def parse_ind_exception(self, dict_in_company, mapping):
        pass

    def parse_ind_violate_law(self, dict_in_company, mapping):
        pass

    def parse_ind_check(self, dict_in_company, mapping):
        pass

    def parse_ent_report(self, dict_in_company, mapping):
        pass

    def parse_ent_contribution(self, dict_in_company, mapping):
        pass

    def parse_ent_change(self, dict_in_company, mapping):
        pass

    def parse_ent_license(self, dict_in_company, mapping):
        pass

    def parse_ent_property(self, dict_in_company, mapping):
        pass

    def parse_ent_sanction(self, dict_in_company, mapping):
        pass

    def parse_other_license(self, dict_in_company, mapping):
        pass

    def parse_other_sanction(self, dict_in_company, mapping):
        pass

    def parse_judical_freeze(self, dict_in_company, mapping):
        pass

    def parse_judical_modify(self, dict_in_company, mapping):
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
