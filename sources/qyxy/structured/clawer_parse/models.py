# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Max


class UpdateByDict(object):
    """数据库操作基本类
    """

    def update_by_dict(self, model, data):
        fields = model._meta.get_all_field_names()
        name = model._meta.db_table
        if name in data:
            enter_id = Basic.objects.all().aggregate(Max('id')).get('id__max')
            data['enter_id'] = enter_id

            for row in data[name]:
                query = model()
                for field in fields:
                    value = row.get(field) or data.get(field)
                    if value is not None:
                        setattr(query, field, value)
                query.save()
                del query

        else:
            for field in fields:
                value = data.get(field)
                if value is not None:
                    setattr(self, field, value)
            self.save()


class Basic(models.Model, UpdateByDict):
    """公司基本类
    """

    credit_code = models.CharField(max_length=20, null=True, blank=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    enter_type = models.CharField(max_length=100, null=True, blank=True)
    corporation = models.CharField(max_length=30, null=True, blank=True)
    register_capital = models.FloatField(null=True)
    establish_date = models.DateField(null=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    time_start = models.DateField(null=True)
    time_end = models.DateField(null=True)
    business_scope = models.TextField(null=True)
    register_gov = models.CharField(max_length=50, null=True, blank=True)
    check_date = models.DateField(null=True)
    register_status = models.CharField(max_length=20, null=True, blank=True)
    register_num = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "basic"


class IndustryCommerceAdministrativePenalty(models.Model, UpdateByDict):
    """工商-行政处罚
    """

    penalty_decision_num = models.IntegerField(null=True)
    illegal_type = models.CharField(max_length=30, null=True, blank=True)
    penalty_content = models.CharField(max_length=50, null=True, blank=True)
    penalty_decision_gov = models.CharField(max_length=50, null=True, blank=True)
    penalty_decision_date = models.DateField(null=True)
    detail = models.CharField(max_length=30, null=True, blank=True)
    penalty_register_date = models.DateField(null=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    creidit_code = models.CharField(max_length=20, null=True, blank=True)
    corporation = models.CharField(max_length=30, null=True, blank=True)
    penalty_publicity_time = models.DateField(null=True)
    enter_id = models.CharField(max_length=30, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industrycommerce_administrative_penalty"


class IndustryCommerceBranch(models.Model, UpdateByDict):
    """工商-分支机构
    """

    enter_code = models.CharField(max_length=20, null=True, blank=True)
    branch_name = models.CharField(max_length=30, null=True, blank=True)
    register_gov = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_branch"


class IndustryCommerceChange(models.Model, UpdateByDict):
    """工商-变更
    """

    modify_item = models.CharField(max_length=30, null=True, blank=True)
    modify_before = models.TextField(null=True, blank=True)
    modify_after = models.TextField(max_length=50, null=True, blank=True)
    modify_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_change"


class IndustryCommerceCheck(models.Model, UpdateByDict):
    """工商-抽查检查
    """

    check_gov = models.CharField(max_length=50, null=True, blank=True)
    check_type = models.CharField(max_length=20, null=True, blank=True)
    check_date = models.DateField(null=True)
    check_result = models.CharField(max_length=50, null=True, blank=True)
    check_comment = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_check"


class IndustryCommerceClear(models.Model, UpdateByDict):
    """工商-清算
    """

    person_in_charge = models.CharField(max_length=30, null=True, blank=True)
    persons = models.CharField(max_length=100, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_clear"


class IndustryCommerceDetailGuarantee(models.Model, UpdateByDict):
    """工商-动产抵押-详情-动产抵押
    """

    register_code = models.CharField(max_length=20, null=True, blank=True)
    sharechange_register_date = models.DateField(null=True)
    register_gov = models.CharField(max_length=50, null=True, blank=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    ind_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_detail_guarantee"


class IndustryCommerceException(models.Model, UpdateByDict):
    """工商-经营异常
    """

    list_on_reason = models.CharField(max_length=100, null=True, blank=True)
    list_on_date = models.DateField(null=True)
    list_out_reason = models.CharField(max_length=100, null=True, blank=True)
    list_out_date = models.DateField(null=True)
    list_gov = models.CharField(max_length=50, null=True, blank=True)
    list_on_gov = models.CharField(max_length=50, null=True, blank=True)
    list_out_gov = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_exception"


class IndustryCommerceIllegal(models.Model, UpdateByDict):
    """工商-严重违法
    """

    list_on_reason = models.CharField(max_length=100, null=True, blank=True)
    list_on_date = models.DateField(null=True)
    list_out_reason = models.CharField(max_length=100, null=True, blank=True)
    list_out_date = models.DateField(max_length=100, null=True, blank=True)
    decision_gov = models.CharField(max_length=30, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_illegal"


class IndustryCommerceMainperson(models.Model, UpdateByDict):
    """工商-主要人员
    """

    name = models.CharField(max_length=30, null=True, blank=True)
    position = models.CharField(max_length=20, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_mainperson"


class IndustryCommerceMortgage(models.Model, UpdateByDict):
    """工商-动产抵押登记
    """

    register_num = models.CharField(max_length=20, null=True, blank=True)
    sharechange_register_date = models.DateField(null=True)
    register_gov = models.CharField(max_length=50, null=True, blank=True)
    guarantee_debt_amount = models.FloatField(null=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    publicity_time = models.DateField(null=True)
    details = models.TextField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_mortgage"


class IndustryCommerceMortgageDetailChange(models.Model, UpdateByDict):
    """工商-抵押-详情-变更
    """

    modify_date = models.DateField(null=True)
    modify_content = models.TextField(null=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    ind_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_mortgage_detail_change"


class IndustryCommerceMortgageDetailGuarantee(models.Model, UpdateByDict):
    """工商-抵押-详情-抵押权人
    """

    check_type = models.CharField(max_length=20, null=True, blank=True)
    amount = models.FloatField(null=True)
    guarantee_scope = models.CharField(max_length=100, null=True, blank=True)
    debtor_duration = models.CharField(max_length=20, null=True, blank=True)
    comment = models.CharField(max_length=100, null=True, blank=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    ind_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_cortgage_detail_guarantee"


class IndustryCommerceMortgageGuaranty(models.Model, UpdateByDict):
    """工商-抵押-详情-抵押物
    """

    name = models.CharField(max_length=30, null=True, blank=True)
    ownership = models.CharField(max_length=30, null=True, blank=True)
    details = models.TextField(null=True)
    coments = models.CharField(max_length=100, null=True, blank=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    ind_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_mortgage_guaranty"


class IndustryCommerceRevoke(models.Model, UpdateByDict):
    """工商-撤销
    """

    revoke_item = models.CharField(max_length=30, null=True, blank=True)
    content_before_revoke = models.CharField(max_length=50, null=True, blank=True)
    content_after_revoke = models.CharField(max_length=50, null=True, blank=True)
    revoke_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_revoke"


class IndustryCommerceShareholders(models.Model, UpdateByDict):
    """工商-股东
    """

    shareholder_type = models.CharField(max_length=20, null=True, blank=True)
    shareholder_name = models.CharField(max_length=30, null=True, blank=True)
    certificate_type = models.CharField(max_length=20, null=True, blank=True)
    certificate_number = models.CharField(max_length=20, null=True, blank=True)
    subscription_amount = models.FloatField(null=True)
    paid_amount = models.FloatField(null=True)
    subscription_type = models.CharField(max_length=30, null=True, blank=True)
    subscription_date = models.DateField(null=True)
    subscription_money_amount = models.FloatField(null=True)
    paid_type = models.CharField(max_length=20, null=True, blank=True)
    paid_money_amount = models.FloatField(null=True)
    paid_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_shareholders"


class IndustryCommerceSharepledge(models.Model, UpdateByDict):
    """
    """

    register_num = models.CharField(max_length=20, null=True, blank=True)
    pledgor = models.CharField(max_length=30, null=True, blank=True)
    pledgor_certificate_code = models.CharField(max_length=20, null=True, blank=True)
    share_pledge_num = models.FloatField(null=True)
    mortgagee = models.CharField(max_length=30, null=True, blank=True)
    mortgagee_certificate_code = models.CharField(max_length=20, null=True, blank=True)
    sharechange_register_date = models.DateField(null=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    change_detail = models.CharField(max_length=100, null=True, blank=True)
    publicity_time = models.DateField(null=True)
    modify_date = models.DateField(null=True)
    modify_content = models.TextField(null=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_commerce_sharepledge"


class IndustryMortgageDetailMortgagee(models.Model, UpdateByDict):
    """工商-抵押-详情-抵押权人
    """

    mortgagee_name = models.CharField(max_length=30, null=True, blank=True)
    mortgagee_certificate_type = models.CharField(max_length=20, null=True, blank=True)
    pledgor_certificate_code = models.CharField(max_length=20, null=True, blank=True)
    register_id = models.CharField(max_length=20, null=True, blank=True)
    ind_id = models.IntegerField(null=True)

    class Meta:
        db_table = "industry_mortgage_detail_mortgagee"


class EnterAdministrativeLicense(models.Model, UpdateByDict):
    """企业-行政许可
    """

    license_num = models.IntegerField(null=True)
    license_filename = models.CharField(max_length=50, null=True, blank=True)
    license_begien_date = models.DateField(null=True)
    license_end_date = models.DateField(null=True)
    license_authority = models.CharField(max_length=30, null=True, blank=True)
    license_content = models.CharField(max_length=50, null=True, blank=True)
    license_status = models.CharField(max_length=20, null=True, blank=True)
    license_detail = models.CharField(max_length=10, null=True, blank=True)
    license_register_time = models.DateField(null=True)
    license_publicity_time = models.DateField(null=True)
    license_change_item = models.CharField(max_length=20, null=True, blank=True)
    license_change_time = models.DateField(null=True)
    license_content_before = models.CharField(max_length=50, null=True, blank=True)
    license_content_after = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "enter_administrative_license"


class EnterAdministrativePenalty(models.Model, UpdateByDict):
    """企业-行政处罚
    """

    penalty_decision_num = models.IntegerField(null=True)
    illegal_type = models.CharField(max_length=30, null=True, blank=True)
    administrative_penalty_content = models.CharField(max_length=30, null=True, blank=True)
    decision_gov = models.CharField(max_length=30, null=True, blank=True)
    decision_date = models.DateField(null=True)
    penalty_comment = models.CharField(max_length=50, null=True, blank=True)
    penalty_publicit_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "enter_administrative_penalty"


class EnterAnnualReport(models.Model, UpdateByDict):
    """企业年报
    """

    report_year = models.IntegerField(null=True)
    publicity_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)
    primary = models.IntegerField(null=True)

    class Meta:
        db_table = "enter_annual_report"


class EnterIntellectualPropertyPledge(models.Model, UpdateByDict):
    """企业-知识产权出质
    """

    credit_code = models.CharField(max_length=20, null=True, blank=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    property_type = models.CharField(max_length=30, null=True, blank=True)
    pledgor_name = models.CharField(max_length=30, null=True, blank=True)
    mortgagee_name = models.CharField(max_length=30, null=True, blank=True)
    mortgage_register_date = models.DateField(null=True)
    property_status = models.CharField(max_length=40, null=True, blank=True)
    property_pledge_change = models.CharField(max_length=40, null=True, blank=True)
    property_pledge_register_gov = models.CharField(max_length=30, null=True, blank=True)
    property_pledge_register_date = models.DateField(null=True)
    property_pledge_publicity_time = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "enter_intellectual_property_pledge"


class EnterModification(models.Model, UpdateByDict):
    """企业-变更
    """

    modify_item = models.CharField(max_length=30, null=True, blank=True)
    modify_before = models.CharField(max_length=50, null=True, blank=True)
    modify_after = models.CharField(max_length=50, null=True, blank=True)
    modify_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "enter_modification"


class EnterSharechange(models.Model, UpdateByDict):
    """企业-股权变更
    """

    shareholder = models.CharField(max_length=30, null=True, blank=True)
    share_ratio_before = models.FloatField(null=True)
    share_ratio_after = models.FloatField(null=True)
    share_change_date = models.DateField(null=True)
    sharechange_register_date = models.DateField(null=True)
    sharechange_publicity_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "enter_sharechange"


class EnterShareholder(models.Model, UpdateByDict):
    """企业-股东及出资
    """

    shareholder_name = models.CharField(max_length=30, null=True, blank=True)
    subscription_amount = models.FloatField(null=True)
    paid_amount = models.FloatField(null=True)
    subscription_type = models.CharField(max_length=20, null=True, blank=True)
    subscription_date = models.DateField(null=True)
    subscription_money_amount = models.FloatField(null=True)
    paid_type = models.CharField(max_length=20, null=True, blank=True)
    paid_money_amount = models.FloatField(null=True)
    paid_date = models.DateField(null=True)
    shareholder_type = models.CharField(max_length=20, null=True, blank=True)
    subscription_publicity_time = models.DateField(null=True)
    paid_publicity_time = models.DateField(null=True)
    publicity_time = models.DateField(null=True)
    modify_time = models.DateField(null=True)
    detals = models.CharField(max_length=256, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "enter_shareholder"


class JudicialShareFreeze(models.Model, UpdateByDict):
    """司法股权冻结
    """

    been_excute_person = models.CharField(max_length=30, null=True, blank=True)
    share_num = models.IntegerField(null=True)
    excute_court = models.CharField(max_length=30, null=True, blank=True)
    notice_num = models.IntegerField(null=True)
    freeze_status = models.CharField(max_length=30, null=True, blank=True)
    freeze_detail = models.CharField(max_length=30, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "judicial_share_freeze"


class JudicialShareholderChange(models.Model, UpdateByDict):
    """司法-司法股东变更登记
    """

    been_excute_name = models.CharField(max_length=30, null=True, blank=True)
    share_num = models.IntegerField(null=True)
    excute_court = models.CharField(max_length=30, null=True, blank=True)
    assignee = models.CharField(max_length=30, null=True, blank=True)
    detail = models.CharField(max_length=30, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "judicial_shareholder_change"


class OtherAdministrativeChange(models.Model, UpdateByDict):
    """其他-行政许可变更
    """

    administrative_change_item = models.CharField(max_length=30, null=True, blank=True)
    administrative_change_tme = models.DateField(null=True)
    administrative_change_before = models.CharField(max_length=50, null=True, blank=True)
    administrative_change_after = models.CharField(max_length=50, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "other_administrative_change"


class OtherAdministrativeLicense(models.Model, UpdateByDict):
    """其他部门-行政许可
    """

    license_file_num = models.IntegerField(null=True)
    license_filename = models.CharField(max_length=50, null=True, blank=True)
    license_begin_date = models.DateField(null=True)
    license_end_date = models.DateField(null=True)
    license_content = models.CharField(max_length=50, null=True, blank=True)
    license_authority_gov = models.CharField(max_length=50, null=True, blank=True)
    license_status = models.CharField(max_length=20, null=True, blank=True)
    license_detail = models.CharField(max_length=20, null=True, blank=True)
    license_valid_date = models.DateField(null=True)
    source = models.CharField(max_length=10, null=True, blank=True)
    update_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "other_administrative_license"


class OtherAdministrativePenalty(models.Model, UpdateByDict):
    """其他部门-行政处罚
    """

    penalty_decision_num = models.IntegerField(null=True)
    illegal_type = models.CharField(max_length=30, null=True, blank=True)
    penalty_content = models.CharField(max_length=50, null=True, blank=True)
    penalty_decision_gov = models.CharField(max_length=50, null=True, blank=True)
    penalty_decision_date = models.DateField(null=True)
    detail = models.CharField(max_length=30, null=True, blank=True)
    penalty_type = models.CharField(max_length=30, null=True, blank=True)
    forfeiture_money = models.FloatField(null=True)
    confiscate_money = models.FloatField(null=True)
    source = models.CharField(max_length=20, null=True, blank=True)
    update_date = models.DateField(null=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "other_administrative_penalty"


class OtherProductionSecurity(models.Model, UpdateByDict):
    """其他-生产安全事故
    """

    accidient_number = models.IntegerField(null=True)
    accident_level = models.IntegerField(null=True)
    accidient_type = models.CharField(max_length=30, null=True, blank=True)
    accidient_time = models.DateField(null=True)
    death_num = models.IntegerField(null=True)
    info_publish_gov = models.CharField(max_length=30, null=True, blank=True)
    enter_id = models.CharField(max_length=20, null=True, blank=True)
    bas_id = models.IntegerField(null=True)

    class Meta:
        db_table = "other_production_security"


class YearReportAssets(models.Model, UpdateByDict):
    """年报-企业资产状况
    """

    asset_all = models.FloatField(null=True)
    owner_asset = models.FloatField(null=True)
    business_income = models.FloatField(null=True)
    profit = models.FloatField(null=True)
    main_business_income = models.FloatField(null=True)
    net_income = models.FloatField(null=True)
    tax = models.FloatField(null=True)
    debts = models.FloatField(null=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_assets"


class YearReportBasic(models.Model, UpdateByDict):
    """年报-基本
    """

    credit_code = models.CharField(max_length=20, null=True, blank=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    enter_phone = models.CharField(max_length=15, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    enter_place = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=20, null=True, blank=True)
    shareholder_change = models.BooleanField(default=False)
    status = models.CharField(max_length=20, null=True, blank=True)
    web_onlinestore = models.BooleanField(default=False)
    staff_number = models.IntegerField(null=True)
    register_num = models.CharField(max_length=20, null=True, blank=True)
    is_warrandice = models.CharField(max_length=10, null=True, blank=True)
    is_invest = models.BooleanField(default=False)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_basic"


class YearReportCorrect(models.Model, UpdateByDict):
    """年报-年报信息更正声明
    """

    correct_item = models.CharField(max_length=30, null=True, blank=True)
    correct_reason = models.CharField(max_length=50, null=True, blank=True)
    correct_time = models.DateField(null=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_correct"


class YearReportInvestment(models.Model, UpdateByDict):
    """年报-对外投资
    """

    invest_enter_name = models.CharField(max_length=50, null=True, blank=True)
    enter_code = models.CharField(max_length=20, null=True, blank=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_investment"


class YearReportModification(models.Model, UpdateByDict):
    """年报-修改记录
    """

    modify_item = models.CharField(max_length=30, null=True, blank=True)
    modify_before = models.CharField(max_length=50, null=True, blank=True)
    modify_after = models.CharField(max_length=50, null=True, blank=True)
    modify_date = models.DateField(null=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_modification"


class YearReportOnline(models.Model, UpdateByDict):
    """年报-网站或网店
    """

    online_type = models.CharField(max_length=20, null=True, blank=True)
    enter_name = models.CharField(max_length=50, null=True, blank=True)
    enter_url = models.CharField(max_length=50, null=True, blank=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_online"


class YearReportSharechange(models.Model, UpdateByDict):
    """年报-股权变更
    """

    shareholder = models.CharField(max_length=20, null=True, blank=True)
    shares_before = models.FloatField(null=True)
    shares_after = models.FloatField(null=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_sharechange"


class YearReportShareholder(models.Model, UpdateByDict):
    """年报-股东及出资
    """

    shareholder = models.CharField(max_length=30, null=True, blank=True)
    subscription_money_amount = models.FloatField(null=True)
    subscription_time = models.DateField(null=True)
    subscription_type = models.CharField(max_length=20, null=True, blank=True)
    paid_money_amount = models.FloatField(null=True)
    paid_time = models.DateField(null=True)
    paid_type = models.CharField(max_length=20, null=True, blank=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_shareholder"


class YearReportWarrandice(models.Model, UpdateByDict):
    """年报-对外提供保证担保
    """

    creditor = models.CharField(max_length=30, null=True, blank=True)
    debtor = models.CharField(max_length=30, null=True, blank=True)
    main_creditor_right = models.CharField(max_length=30, null=True, blank=True)
    main_creditor_right_amount = models.FloatField(null=True)
    fullfill_debt_duration = models.CharField(max_length=30, null=True, blank=True)
    guarantee_duration = models.CharField(max_length=30, null=True, blank=True)
    guarantee_type = models.CharField(max_length=30, null=True, blank=True)
    warrandice_scope = models.CharField(max_length=100, null=True, blank=True)
    year_report_id = models.CharField(max_length=20, null=True, blank=True)
    ent_id = models.IntegerField(null=True)

    class Meta:
        db_table = "year_report_warrandice"
