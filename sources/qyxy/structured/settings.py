# -*- coding: utf-8 -*-
from datetime import date

# mysql configs
mysql_confs = {
    'host': "localhost",
    'user': "root",
    'passwd': "ChuHuimin1990",
    'db': "clawer",
    'port': 3306,
}

# SQL
sqls = {}
sqls['basic_select_is_exist'] = """
SELECT
    id
FROM
    basic
WHERE
    credit_code = %(credit_code)s and enter_name = %(enter_name)s
"""

sqls['basic_select_id'] = """
SELECT
    id
FROM
    basic
ORDER BY
    id
DESC
LIMIT 1
"""

sqls['basic_update'] = """
UPDATE
    basic
SET
    credit_code = %(credit_code)s,
    enter_name = %(enter_name)s,
    enter_type = %(enter_type)s,
    corporation = %(corporation)s,
    register_capital = %(register_capital)s,
    establish_date = %(establish_date)s,
    place = %(place)s,
    time_start = %(time_start)s,
    time_end = %(time_end)s,
    business_scope = %(business_scope)s,
    register_gov = %(register_gov)s,
    check_date = %(check_date)s,
    register_status = %(register_status)s,
    register_num = %(register_num)s
WHERE
    id = %(id)s
"""

sqls['basic_insert'] = """
INSERT INTO basic(
    credit_code, enter_name, enter_type,
    corporation, register_capital,
    establish_date, place, time_start,
    time_end, business_scope, register_gov,
    check_date, register_status,
    register_num, id
)
VALUES
    (
    %(credit_code)s, %(enter_name)s, %(enter_type)s,
    %(corporation)s, %(register_capital)s,
    %(establish_date)s, %(place)s, %(time_start)s,
    %(time_end)s, %(business_scope)s, %(register_gov)s,
    %(check_date)s, %(register_status)s,
    %(register_num)s, %(id)s
    )
"""

# mysql fields
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
