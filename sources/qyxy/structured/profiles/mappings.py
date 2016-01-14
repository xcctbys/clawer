# -*- coding: utf-8 -*-

mappings = {}

mappings["ind_comm_pub_reg_basic"] = {
    "注册资本": "register_capital",
    "经营范围": "business_scope",
    "注册号/统一社会信用代码": "credit_code",
    "营业期限至": "time_end",
    "成立日期": "time_start",
    "注册号": "register_num",
    "住所": "place",
    "名称": "enter_name",
    "核准日期": "check_date",
    "类型": "enter_type",
    "登记状态": "register_status",
    "法定代表人": "corporation",
    "登记机关": "register_gov",
    "营业期限自": "time_start",
}

mappings["ind_comm_pub_reg_shareholder"] = {
    "股东类型": "shareholder_type",
    "证照/证件号码": "certificate_number",
    "认缴出资日期": "subscription_date",
    "认缴额（万元）": "subscription_amount",
    "认缴出资方式": "subscription_type",
    "认缴出资额（万元）": "subscription_money_amount",
    "实缴出资方式": "paid_type",
    "实缴额（万元）": "paid_amount",
    "实缴出资日期": "paid_date",
    "实缴出资额（万元）": "paid_money_amount",
    "股东": "shareholder_name",
    "证照/证件类型": "certificate_type",
}

mappings["ind_comm_pub_reg_modify"] = {
    "变更事项": "modify_item",
    "变更日期": "modify_date",
    "变更后内容": "modify_after",
    "变更前内容": "modify_before",
}

mappings["ind_comm_pub_arch_key_persons"] = {
    "序号": "enter_id",
    "姓名": "name",
    "职务": "postion",
}

mappings["ind_comm_pub_arch_branch"] = {
    "序号": "enter_id",
    "登记机关": "register_gov",
    "注册号/统一社会信用代码": "enter_code",
    "名称": "branch_name",
}

"ind_comm_pub_arch_liquidation": {
    "清算组成员": "persons",
    "清算组负责人": "person_in_change"
},
"ind_comm_pub_movable_property_reg": {
    "状态": "status",
    "公示日期": "publicity_time",
    "登记日期": "sharechange_register_date",
    "登记编号": "register_num",
    "被担保债权数额": "guarantee_debt_amount",
    "序号": "enter_id",
    "登记机关": "register_gov"
},
"ind_comm_pub_equity_ownership_reg": {
    "出质股权数额": "share_pledge_num",
    "公示日期": "publicity_time",
    "状态": "status",
    "质权人": "mortgagee",
    "股权出质设立登记日期": "2015年12月24日",
    "出质人": "pledgor",
    "登记编号": "register_num",
    "证照/证件号码": "pledgor_certificate_code",
    "变化情况": "change_detail",
    "序号": "id"
},
"ind_comm_pub_administration_sanction": {
    "行政处罚内容": "penalty_content",
    "公示日期": "penalty_publicit_date",
    "作出行政处罚决定机关名称": "penalty_decision_gov",
    "违法行为类型": "illegal_type",
    "作出行政处罚决定日期": "penalty_decision_date",
    "详情": "detail",
    "行政处罚决定书文号": "penalty_decision_num",
    "序号": "id"
},
"ind_comm_pub_business_exception": {
    "公示日期": null,
    "移出经营异常名录原因": "list_out_reason",
    "作出决定机关": "list_gov",
    "列入经营异常名录原因": "list_on_reason",
    "列入日期": "list_on_date",
    "移出日期": "list_out_date",
    "序号": "id"
},
"ind_comm_pub_serious_violate_law": {
    "移出严重违法企业名单原因": "list_out_reason",
    "列入严重违法企业名单原因": "list_on_reason",
    "公示日期": null,
    "作出决定机关": "decision_gov",
    "列入日期": "list_on_date",
    "移出日期": "list_out_date",
    "序号": "id"
},
"ind_comm_pub_spot_check": {
    "检查实施机关": "check_gov",
    "公示日期": null,
    "结果": "check_result",
    "类型": "check_type",
    "日期": "check_date",
    "序号": "id"
},

  "ent_pub_ent_annual_report": {},
  "ent_pub_shareholder_capital_contribution": {
      "认缴出资日期": "subscription_date",
      "认缴额（万元）": "subscription_amount",
      "认缴出资方式": "subscription_type",
      "认缴出资额（万元）": "subscription_money_amount",
      "公示日期": "publicity_time",
      "实缴额（万元）": "paid_amount",
      "股东（发起人）": "shareholder_name",
      "实缴明细": null,
      "认缴明细": null,
      "实缴出资日期": "paid_date",
      "实缴出资方式": "paid_type",
      "实缴出资额（万元）": "paid_money_amount"
  },
  "ent_pub_equity_change": {
      "变更前股权比例": "share_ratio_before",
      "公示日期": "sharechange_publicity_date",
      "股权变更日期": "share_change_date",
      "变更后股权比例": "share_ratio_after",
      "序号": "id",
      "股东": "shareholder"
  },
  "ent_pub_administration_license": {
      "状态": "license_status",
      "有效期至": "license_end_date",
      "公示日期": "license_publicity_time",
      "许可内容": "license_content",
      "许可文件名称": "license_filename",
      "许可文件编号": "license_num",
      "详情": "license_detail",
      "序号": "id",
      "许可机关": "license_authority",
      "有效期自": "license_begien_date"
  },
  "ent_pub_knowledge_property": {
      "状态": "property_status",
      "公示日期": "property_pledge_publicity_time",
      "注册号": "credit_code",
      "质权登记期限": "mortgage_register_date",
      "出质人名称": "pledgor_name",
      "变化情况": "property_pledge_change",
      "质权人名称": "mortgagee_name",
      "名称": "enter_name",
      "序号": "property_type",
      "种类": "id"
  },
  "ent_pub_administration_sanction": {
      "行政处罚内容": "administrative_penalty_content",
      "公示日期": "penalty_publicity_time",
      "作出行政处罚决定机关名称": "decision_gov",
      "违法行为类型": "illegal_type",
      "作出行政处罚决定日期": "decision_date",
      "行政处罚决定书文号": "penalty_decision_num",
      "序号": "id",
      "备注": "penalty_comment",
      "详情":"detail"
  },

  "other_dept_pub_administration_license": {
      "状态": "license_status",
      "有效期至": "license_end_date",
      "许可内容": "license_content",
      "许可文件名称": "license_filename",
      "许可文件编号": "license_file_num",
      "详情": "license_detail",
      "序号": "id",
      "许可机关": "license_authority_gov",
      "有效期自": "license_begin_date"
  },
  "other_dept_pub_administration_sanction": {
      "行政处罚内容": "administrative_penalty_content",
      "作出行政处罚决定机关名称": "decision_gov",
      "违法行为类型": "illegal_type",
      "作出行政处罚决定日期": "decision_date",
      "行政处罚决定书文号": "penalty_decision_num",
      "序号": "id",
      "详情":"detail"
  },

  "judical_assist_pub_equity_freeze": {
      "状态": "freeze_status",
      "被执行人": "been_excute_person",
      "股权数额": "share_num",
      "详情": "freeze_detail",
      "序号": "id",
      "执行法院": "excute_court",
      "协助公示通知书文号": "notice_num"
  },
  "judical_assist_pub_shareholder_modify": {
      "被执行人": "been_excute_name",
      "股权数额": "share_num",
      "详情": "detail",
      "序号": "id",
      "执行法院": "excute_court",
      "受让人": "assignee"
  }
  }
