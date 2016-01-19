# -*- coding: utf-8 -*-

mappings = {}

mappings['ind_comm_pub_reg_basic'] = {
    u'注册资本': 'register_capital',
    u'经营范围': 'business_scope',
    u'注册号/统一社会信用代码': 'credit_code',
    u'营业期限至': 'time_end',
    u'成立日期': 'time_start',
    u'注册号': 'register_num',
    u'住所': 'place',
    u'名称': 'enter_name',
    u'核准日期': 'check_date',
    u'类型': 'enter_type',
    u'登记状态': 'register_status',
    u'法定代表人': 'corporation',
    u'登记机关': 'register_gov',
    u'营业期限自': 'time_start',
}

mappings['ind_comm_pub_reg_shareholder'] = {
    u'股东类型': 'shareholder_type',
    u'证照/证件号码': 'certificate_number',
    u'认缴出资日期': 'subscription_date',
    u'认缴额（万元）': 'subscription_amount',
    u'认缴出资方式': 'subscription_type',
    u'认缴出资额（万元）': 'subscription_money_amount',
    u'实缴出资方式': 'paid_type',
    u'实缴额（万元）': 'paid_amount',
    u'实缴出资日期': 'paid_date',
    u'实缴出资额（万元）': 'paid_money_amount',
    u'股东': 'shareholder_name',
    u'证照/证件类型': 'certificate_type',
}

mappings['ind_comm_pub_reg_modify'] = {
    u'变更事项': 'modify_item',
    u'变更日期': 'modify_date',
    u'变更后内容': 'modify_after',
    u'变更前内容': 'modify_before',
}

mappings['ind_comm_pub_arch_key_persons'] = {
    u'序号': 'bas_id',
    u'姓名': 'name',
    u'职务': 'postion',
}

mappings['ind_comm_pub_arch_branch'] = {
    u'序号': 'bas_id',
    u'登记机关': 'register_gov',
    u'注册号/统一社会信用代码': 'enter_code',
    u'名称': 'branch_name',
}

mappings['ind_comm_pub_arch_liquidation'] = {
    u'清算组成员': 'persons',
    u'清算组负责人': 'person_in_change',
}

mappings['ind_comm_pub_movable_property_reg'] = {
    u'状态': 'status',
    u'公示日期': 'publicity_time',
    u'登记日期': 'sharechange_register_date',
    u'登记编号': 'register_num',
    u'被担保债权数额': 'guarantee_debt_amount',
    u'序号': 'bas_id',
    u'登记机关': 'register_gov',
}

mappings['ind_comm_pub_equity_ownership_reg'] = {
    u'出质股权数额': 'share_pledge_num',
    u'公示日期': 'publicity_time',
    u'状态': 'status',
    u'质权人': 'mortgagee',
    u'股权出质设立登记日期': None,
    u'出质人': 'pledgor',
    u'登记编号': 'register_num',
    u'证照/证件号码': 'pledgor_certificate_code',
    u'变化情况': 'change_detail',
    u'序号': 'id',
}

mappings['ind_comm_pub_administration_sanction'] = {
    u'行政处罚内容': 'penalty_content',
    u'公示日期': 'penalty_publicit_date',
    u'作出行政处罚决定机关名称': 'penalty_decision_gov',
    u'违法行为类型': 'illegal_type',
    u'作出行政处罚决定日期': 'penalty_decision_date',
    u'详情': 'detail',
    u'行政处罚决定书文号': 'penalty_decision_num',
    u'序号': 'id',
}

mappings['ind_comm_pub_business_exception'] = {
    u'公示日期': None,
    u'移出经营异常名录原因': 'list_out_reason',
    u'作出决定机关': 'list_gov',
    u'列入经营异常名录原因': 'list_on_reason',
    u'列入日期': 'list_on_date',
    u'移出日期': 'list_out_date',
    u'序号': 'id',
}

mappings['ind_comm_pub_serious_violate_law'] = {
    u'移出严重违法企业名单原因': 'list_out_reason',
    u'列入严重违法企业名单原因': 'list_on_reason',
    u'公示日期': None,
    u'作出决定机关': 'decision_gov',
    u'列入日期': 'list_on_date',
    u'移出日期': 'list_out_date',
    u'序号': 'id',
}

mappings['ind_comm_pub_spot_check'] = {
    u'检查实施机关': 'check_gov',
    u'公示日期': None,
    u'结果': 'check_result',
    u'类型': 'check_type',
    u'日期': 'check_date',
    u'序号': 'id',
}

mappings['ent_pub_ent_annual_report'] = {}

mappings['ent_pub_shareholder_capital_contribution'] = {
    u'认缴出资日期': 'subscription_date',
    u'认缴额（万元）': 'subscription_amount',
    u'认缴出资方式': 'subscription_type',
    u'认缴出资额（万元）': 'subscription_money_amount',
    u'公示日期': 'publicity_time',
    u'实缴额（万元）': 'paid_amount',
    u'股东（发起人）': 'shareholder_name',
    u'实缴明细': None,
    u'认缴明细': None,
    u'实缴出资日期': 'paid_date',
    u'实缴出资方式': 'paid_type',
    u'实缴出资额（万元）': 'paid_money_amount',
}

mappings['ent_pub_equity_change'] = {
    u'变更前股权比例': 'share_ratio_before',
    u'公示日期': 'sharechange_publicity_date',
    u'股权变更日期': 'share_change_date',
    u'变更后股权比例': 'share_ratio_after',
    u'序号': 'id',
    u'股东': 'shareholder',
}

mappings['ent_pub_administration_license'] = {
    u'状态': 'license_status',
    u'有效期至': 'license_end_date',
    u'公示日期': 'license_publicity_time',
    u'许可内容': 'license_content',
    u'许可文件名称': 'license_filename',
    u'许可文件编号': 'license_num',
    u'详情': 'license_detail',
    u'序号': 'id',
    u'许可机关': 'license_authority',
    u'有效期自': 'license_begien_date',
}

mappings['ent_pub_knowledge_property'] = {
    u'状态': 'property_status',
    u'公示日期': 'property_pledge_publicity_time',
    u'注册号': 'credit_code',
    u'质权登记期限': 'mortgage_register_date',
    u'出质人名称': 'pledgor_name',
    u'变化情况': 'property_pledge_change',
    u'质权人名称': 'mortgagee_name',
    u'名称': 'enter_name',
    u'序号': 'property_type',
    u'种类': 'id',
}

mappings['ent_pub_administration_sanction'] = {
    u'行政处罚内容': 'administrative_penalty_content',
    u'公示日期': 'penalty_publicity_time',
    u'作出行政处罚决定机关名称': 'decision_gov',
    u'违法行为类型': 'illegal_type',
    u'作出行政处罚决定日期': 'decision_date',
    u'行政处罚决定书文号': 'penalty_decision_num',
    u'序号': 'id',
    u'备注': 'penalty_comment',
    u'详情': 'detail',
}

mappings['other_dept_pub_administration_license'] = {
    u'状态': 'license_status',
    u'有效期至': 'license_end_date',
    u'许可内容': 'license_content',
    u'许可文件名称': 'license_filename',
    u'许可文件编号': 'license_file_num',
    u'详情': 'license_detail',
    u'序号': 'id',
    u'许可机关': 'license_authority_gov',
    u'有效期自': 'license_begin_date',
}

mappings['other_dept_pub_administration_sanction'] = {
    u'行政处罚内容': 'administrative_penalty_content',
    u'作出行政处罚决定机关名称': 'decision_gov',
    u'违法行为类型': 'illegal_type',
    u'作出行政处罚决定日期': 'decision_date',
    u'行政处罚决定书文号': 'penalty_decision_num',
    u'序号': 'id',
    u'详情': 'detail',
}

mappings['judical_assist_pub_equity_freeze'] = {
    u'状态': 'freeze_status',
    u'被执行人': 'been_excute_person',
    u'股权数额': 'share_num',
    u'详情': 'freeze_detail',
    u'序号': 'id',
    u'执行法院': 'excute_court',
    u'协助公示通知书文号': 'notice_num',
}

mappings['judical_assist_pub_shareholder_modify'] = {
    u'被执行人': 'been_excute_name',
    u'股权数额': 'share_num',
    u'详情': 'detail',
    u'序号': 'id',
    u'执行法院': 'excute_court',
    u'受让人': 'assignee',
}