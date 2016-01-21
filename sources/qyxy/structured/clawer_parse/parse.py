# -*- coding: utf-8 -*-

import json
import time
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
    EnterAdministrativeLicense,
    EnterAdministrativePenalty,
    EnterAnnualReport,
    EnterIntellectualPropertyPledge,
    EnterModification,
    EnterSharechange,
    EnterShareholder,
    JudicialShareFreeze,
    JudicialShareholderChange,
    OtherAdministrativeChange,
    OtherAdministrativeLicense,
    OtherAdministrativePenalty,
    OtherProductionSecurity,
    YearReportAssets,
    YearReportBasic,
    YearReportCorrect,
    YearReportInvestment,
    YearReportModification,
    YearReportOnline,
    YearReportSharechange,
    YearReportShareholder,
    YearReportWarrandice,
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
        begin = time.time()

        for register_num in self.companies:
            company = self.companies[register_num]
            print u"\n公司注册Id: %s" % register_num
            self.parse_company(company, register_num)
            handled_num = handled_num + 1

        end = time.time()
        secs = int(round((end - begin) * 1000))
        print u"\n=== 共导入%d个公司的数据，耗时%dms ===" % (handled_num, secs)

    def parse_company(self, company={}, register_num=0):
        keys = self.keys

        self.company_result = {}

        for key in company:
            if type(company[key]) == dict:
                if key in keys and key in mappings:
                    self.parse_dict(company[key], mappings[key])
            elif type(company[key] == list):
                if key in keys and key in mappings:
                    self.parse_list(key, company[key], mappings[key])

        credit_code = self.company_result.get('credit_code')
        if credit_code is None:
            credit_code = register_num
        if self.company_result.get('register_num') is None:
            self.company_result['register_num'] = register_num

        self.conversion_type()
        self.write_to_mysql()
        self.company_result = {}

    def parse_dict(self, dict_in_company, mapping):
        for field in dict_in_company:
            if field in mapping:
                self.company_result[mapping[field]] = dict_in_company[field]

    def parse_list(self, key, list_in_company, mapping):
        keys_to_tables = consts.keys_to_tables
        special_parse_keys = consts.special_parse_keys
        name = keys_to_tables.get(key)
        parse_func = self.key_to_parse_function(key)
        if key not in special_parse_keys:
            for d in list_in_company:
                value = parse_func(d, mapping)
                if name is not None and value is not None:
                    if self.company_result.get(name) is None:
                        self.company_result[name] = []
                    self.company_result[name].append(value)
        elif key == special_parse_keys[0]:
            for d in list_in_company:
                value = parse_func(d, mapping)
                if name is not None and value is not None:
                    if self.company_result.get(name) is None:
                        self.company_result[name] = []
                    self.company_result[name] = value
        elif key == special_parse_keys[1]:
            for d in list_in_company:
                value = parse_func(d, mapping)
                if name is not None and value is not None:
                    self.company_result[name] = value
        else:
            for d in list_in_company:
                parse_func(d, mapping)

    def key_to_parse_function(self, key):
        keys_to_functions = {
            "ind_comm_pub_reg_shareholder": self.parse_ind_shareholder,
            "ind_comm_pub_reg_modify": self.parse_general,
            "ind_comm_pub_arch_key_persons": self.parse_general,
            "ind_comm_pub_arch_branch": self.parse_general,
            "ind_comm_pub_movable_property_reg": self.parse_general,
            "ind_comm_pub_equity_ownership_reg": self.parse_general,
            "ind_comm_pub_administration_sanction": self.parse_general,
            "ind_comm_pub_business_exception": self.parse_general,
            "ind_comm_pub_serious_violate_law": self.parse_general,
            "ind_comm_pub_spot_check": self.parse_general,
            "ent_pub_ent_annual_report": self.parse_ent_report,
            "ent_pub_shareholder_capital_contribution": self.parse_general,
            "ent_pub_equity_change": self.parse_general,
            "ent_pub_administration_license": self.parse_general,
            "ent_pub_knowledge_property": self.parse_general,
            "ent_pub_administration_sanction": self.parse_general,
            "other_dept_pub_administration_license": self.parse_general,
            "other_dept_pub_administration_sanction": self.parse_general,
            "judical_assist_pub_equity_freeze": self.parse_general,
            "judical_assist_pub_shareholder_modify": self.parse_general,
        }
        return keys_to_functions.get(key, lambda: "noting")

    def parse_general(self, dict_in_company, mapping):
        result = {}
        for field in dict_in_company:
            if field in mapping and dict_in_company[field] is not None:
                result[mapping[field]] = dict_in_company[field]
        return result

    def parse_ind_shareholder(self, dict_in_company, mapping):
        result = []
        dict_inner = {}
        print "parse_ind_shareholder"
        for field, value in dict_in_company.iteritems():
            if field == u"详情":
                if value is not None:
                    # for dic in value:
                    #     print dic
                    for key_add in value:
                        #print key_add
                        if key_add is not None:
                            list_in = value[key_add]
                            for dict_in in list_in:
                                for key_in in dict_in:
                                    if key_in ==u"list":
                                        for dict_fuck in dict_in[key_in]:
                                            for key_fuck in dict_fuck:
                                                dict_inner[mapping.get(key_fuck)] = dict_fuck[key_fuck]
                                            result.append(dict_inner)
                                            dict_inner = {}
                                    else:
                                        if result is None:
                                            dict_inner[mapping.get(key_in)] = dict_in[key_in]
                                            result.append(dict_inner)
                                            dict_inner = None
                                        else:
                                            for result_dict in result: 
                                                result_dict[mapping.get(key_in)] = dict_in[key_in]
                        else:
                            result.append(dict_inner)
                            dict_inner = {}
        for field, value in dict_in_company.iteritems():
            #print field, value
            if field == u"详情":
                pass
            else:
                #print field, value
                if not result:
                    #print field, value
                    dict_inner[mapping.get(field)] = value
                    result.append(dict_inner)
                    dict_inner = {}
                    #print field
                else:
                    pass
        return result

    def parse_ent_report(self, dict_in_company, mapping):
        pass
        # ent_report = {}
        # for key, value in dict_in_company.iteritems():
        #     type_value = type(value)
        #     if type_value == unicode or type_value == str:
        #         ent_report[mapping[key]] = value
        #     else:
        #         year_report_id = ent_report.get('year_report_id')
        #         self.parse_report_details(year_report_id, value, mapping[key])

        # name = keys_to_tables.get('ent_pub_ent_annual_report')
        # if not self.company_result[name]:
        #     self.company_result[name] = []
        # self.company_result[name].append(ent_report)

    def parse_report_details(self, year_report_id, details, mapping):
        keys_to_tables = consts.keys_to_tables

        for key, value in details.iteritems():
            name = keys_to_tables.get(key)
            if type(value) == list:
                pass
            else:
                report = {}
                for field, value in details.iteritems():
                    report[mapping[key]] = value


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
        self.update(EnterAdministrativeLicense)
        self.update(EnterAdministrativePenalty)
        self.update(EnterAnnualReport)
        self.update(EnterIntellectualPropertyPledge)
        self.update(EnterModification)
        self.update(EnterSharechange)
        self.update(EnterShareholder)
        self.update(JudicialShareFreeze)
        self.update(JudicialShareholderChange)
        self.update(OtherAdministrativeChange)
        self.update(OtherAdministrativeLicense)
        self.update(OtherAdministrativePenalty)
        self.update(OtherProductionSecurity)
        self.update(YearReportAssets)
        self.update(YearReportBasic)
        self.update(YearReportCorrect)
        self.update(YearReportInvestment)
        self.update(YearReportModification)
        self.update(YearReportOnline)
        self.update(YearReportSharechange)
        self.update(YearReportShareholder)
        self.update(YearReportWarrandice)

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
                for d in value:
                    for d_field in d:
                        d_value = d[d_field]
                        if d_field in type_date and d_value is not None:
                            d[d_field] = to_date(d_value.encode('utf-8'))
                        elif d_field in type_float and d_value is not None and type(d_value) == unicode:
                            d[d_field] = to_float(d_value.encode('utf-8'))
