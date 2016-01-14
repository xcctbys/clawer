# -*- coding: utf-8 -*-
from datetime import date

fields = {}
fields['basic_data'] = {
    'credit_code': 1000,
    'enter_name': u"普林科技",
    'enter_type': "",
    'corporation': "",
    'register_capital': 100.0,
    'establish_date': date(2016, 1, 13),
    'place': "1+1",
    'time_start': date(2016, 1, 13),
    'time_end': date(2016, 1, 13),
    'business_scope': "",
    'register_gov': "",
    'check_date': date(2016, 1, 13),
    'register_status': "",
    'register_num': "",
    'id': 0,
}

# to handle one company's json keys
keys = [
    "ind_comm_pub_reg_basic",
    "ind_comm_pub_reg_shareholder",
    "ind_comm_pub_reg_modify",
    "ind_comm_pub_arch_key_persons",
    "ind_comm_pub_arch_branch",
    "ind_comm_pub_arch_liquidation",
    "ind_comm_pub_movable_property_reg",
]

"""
"ind_comm_pub_equity_ownership_reg",
"ind_comm_pub_administration_sanction",
"ind_comm_pub_business_exception",
"ind_comm_pub_serious_violate_law",
"ind_comm_pub_spot_check",
"""
