# -*- coding: utf-8 -*-
from datetime import date

# mysql configs
mysql_confs = {
    'host': "localhost",
    'user': "root",
    'passwd': "",
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

sqls['industry_commerce_mortgage_insert'] = """
INSERT INTO industry_commerce_mortgage(
    register_num, sharechange_register_date,
    register_gov, guarantee_debt_amount,
    status, publicity_time, details,
    enter_id, id, bas_id
)
VALUES
    (
        [value-1], [value-2], [value-3], [value-4],
        [value-5], [value-6], [value-7],
        [value-8], [value-9], [value-10]
    )
"""

sqls['industry_commerce_mortgage_update'] = """
UPDATE
    industry_commerce_mortgage
SET
    register_num = [value-1],
    sharechange_register_date = [value-2],
    register_gov = [value-3],
    guarantee_debt_amount = [value-4],
    status = [value-5],
    publicity_time = [value-6],
    details = [value-7],
    enter_id = [value-8],
    id = [value-9],
    bas_id = [value-10]
WHERE
    1
"""

sqls['industry_commerce_mortgage_detail_change_insert'] = """
INSERT INTO industry_commerce_mortgage_detail_change(
    modify_date, modify_content,
    register_id, id, ind_id
)
VALUES
    (
        [value-1], [value-2], [value-3], [value-4],
        [value-5]
    )
"""

sqls['industry_commerce_mortgage_detail_change_update'] = """
UPDATE
    industry_commerce_mortgage_detail_change
SET
    modify_date = [value-1],
    modify_content = [value-2],
    register_id = [value-3],
    id = [value-4],
    ind_id = [value-5]
WHERE
    1
"""

sqls['industry_commerce_mortgage_detail_guarantee_insert'] = """
INSERT INTO industry_commerce_mortgage_detail_guarantee(
    check_type, amount, guarantee_scope,
    debtor_duration, comment, register_id,
    id, ind_id
)
VALUES
    (
        [value-1], [value-2], [value-3], [value-4],
        [value-5], [value-6], [value-7],
        [value-8]
    )
"""

sqls['industry_commerce_mortgage_detail_guarantee_update'] = """
UPDATE
    industry_commerce_mortgage_detail_guarantee
SET
    check_type = [value-1],
    amount = [value-2],
    guarantee_scope = [value-3],
    debtor_duration = [value-4],
    comment = [value-5],
    register_id = [value-6],
    id = [value-7],
    ind_id = [value-8]
WHERE
    1
"""

sqls['industry_commerce_mortgage_guaranty_insert'] = """
INSERT INTO industry_commerce_mortgage_guaranty(
    name, ownership, details, coments,
    register_id, id, ind_id
)
VALUES
    (
        [value-1], [value-2], [value-3], [value-4],
        [value-5], [value-6], [value-7]
    )
"""

sqls['industry_commerce_mortgage_guaranty_update'] = """
UPDATE
    industry_commerce_mortgage_guaranty
SET
    name = [value-1],
    ownership = [value-2],
    details = [value-3],
    coments = [value-4],
    register_id = [value-5],
    id = [value-6],
    ind_id = [value-7]
WHERE
    1
"""

sqls['industry_commerce_revoke_insert'] = """
INSERT INTO industry_commerce_revoke(
    revoke_item, content_before_revoke,
    content_after_revoke, revoke_date,
    enter_id, id, bas_id
)
VALUES
    (
        [value-1], [value-2], [value-3], [value-4],
        [value-5], [value-6], [value-7]
    )
"""

sqls['industry_commerce_revoke_update'] = """
UPDATE
    industry_commerce_revoke
SET
    revoke_item = [value-1],
    content_before_revoke = [value-2],
    content_after_revoke = [value-3],
    revoke_date = [value-4],
    enter_id = [value-5],
    id = [value-6],
    bas_id = [value-7]
WHERE
    1
"""

sqls['industry_commerce_shareholders_insert'] = """
INSERT INTO industry_commerce_shareholders(
    shareholder_type, shareholder_name,
    certificate_type, certificate_number,
    subscription_amount, paid_amount,
    subscription_type, subscription_date,
    subscription_money_amount, paid_type,
    paid_money_amount, paid_date,
    enter_id, id, bas_id
)
VALUES
    (
        [value-1], [value-2], [value-3], [value-4],
        [value-5], [value-6], [value-7],
        [value-8], [value-9], [value-10],
        [value-11], [value-12], [value-13],
        [value-14], [value-15]
    )
"""

sqls['industry_commerce_shareholders_update'] = """
UPDATE
    industry_commerce_shareholders
SET
    shareholder_type = [value-1],
    shareholder_name = [value-2],
    certificate_type = [value-3],
    certificate_number = [value-4],
    subscription_amount = [value-5],
    paid_amount = [value-6],
    subscription_type = [value-7],
    subscription_date = [value-8],
    subscription_money_amount = [value-9],
    paid_type = [value-10],
    paid_money_amount = [value-11],
    paid_date = [value-12],
    enter_id = [value-13],
    id = [value-14],
    bas_id = [value-15]
WHERE
    1
"""

sqls['industry_commerce_sharepledge_insert'] = """
INSERT INTO industry_commerce_sharepledge(
    register_num, pledgor, pledgor_certificate_code,
    share_pledge_num, mortgagee,
    mortgagee_certificate_code, sharechange_register_date,
    status, change_detail, publicity_time,
    modify_date, modify_content,
    register_id, id, bas_id
)
VALUES
    (
        [value-1], [value-2], [value-3], [value-4],
        [value-5], [value-6], [value-7],
        [value-8], [value-9], [value-10],
        [value-11], [value-12], [value-13],
        [value-14], [value-15]
    )
"""

sqls['industry_commerce_sharepledge_insert'] = """
UPDATE
    industry_commerce_sharepledge
SET
    register_num = [value-1],
    pledgor = [value-2],
    pledgor_certificate_code = [value-3],
    share_pledge_num = [value-4],
    mortgagee = [value-5],
    mortgagee_certificate_code = [value-6],
    sharechange_register_date = [value-7],
    status = [value-8],
    change_detail = [value-9],
    publicity_time = [value-10],
    modify_date = [value-11],
    modify_content = [value-12],
    register_id = [value-13],
    id = [value-14],
    bas_id = [value-15]
WHERE
    1
"""

sqls['industry_mortgage_detail_mortgagee_insert'] = """
INSERT INTO industry_mortgage_detail_mortgagee(
    mortgagee_name, mortgagee_certificate_type,
    pledgor_certificate_code, register_id,
    id, ind_id
)
VALUES
    (
        [value-1], [value-2], [value-3], [value-4],
        [value-5], [value-6]
    )
"""

sqls['industry_mortgage_detail_mortgagee_update'] = """
UPDATE
    industry_mortgage_detail_mortgagee
SET
    mortgagee_name = [value-1],
    mortgagee_certificate_type = [value-2],
    pledgor_certificate_code = [value-3],
    register_id = [value-4],
    id = [value-5],
    ind_id = [value-6]
WHERE
    1
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
