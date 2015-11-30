#!/usr/bin/env python
#encoding=utf-8

import os
import sys
from bs4 import BeautifulSoup
from analyzer import Analyzer
class AnalyzerBeijingEnt(Analyzer):
    def __init__(self):
        super(self.__class__).__init__(self)

    def analyze_work(self, path):
        pass

    def analyze_ind_comm_pub_pages(self, path):
        pass

    def analyze_ent_pub_pages(self, path):
        pass

    def analyze_other_dept_pub_pages(self, path):
        pass

    def analyze_downloaded_page(self, type):
        pass

    def analyze_judical_assist_pages(self, path):
        pass

    #工商公示信息-注册信息-基本信息
    def analyze_ind_comm_pub_reg_basic_page(self, page, json_obj):
        soup = BeautifulSoup(page)
        
        pass

    #工商公示信息-注册信息-股东信息
    def analyze_ind_comm_pub_reg_shareholder_page(self, page, json_obj):
        pass

    #工商公示信息-注册信息-变更信息
    def analyze_ind_comm_pub_reg_modify_page(self, page, json_obj):
        pass

    #工商公示信息-备案信息-主要人员信息
    def analyze_ind_comm_pub_arch_key_persons_page(self, page, json_obj):
        pass

    #工商公示信息-备案信息-分支机构信息
    def analyze_ind_comm_pub_arch_branch_page(self, page, json_obj):
        pass

    #工商公示信息-备案信息-清算信息
    def analyze_ind_comm_pub_arch_liquidation_page(self, page, json_obj):
        pass
