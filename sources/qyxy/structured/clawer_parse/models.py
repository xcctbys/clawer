from django.db import models


class Basic(models.Model):
    """公司基本类
    """

    credit_code = models.CharField(max_length=20)
    enter_name = models.CharField(max_length=50)
    enter_type = models.CharField(max_length=20)
    corporation = models.CharField(max_length=30)
    register_capital = models.FloatField()
    establish_date = models.DateTimeField()
    place = models.CharField(max_length=100)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    business_scope = models.TextField()
    register_gov = models.CharField(max_length=50)
    check_date = models.DateTimeField()
    register_status = models.CharField(max_length=20)
    register_num = models.CharField(max_length=20)


class IndustrycommerceAdministrativePenalty(models.Model):
    """工商-行政处罚
    """

    penalty_decision_num = models.IntField()
    illegal_type = models.CharField(max_length=30)
    penalty_content = models.CharField(max_length=50)
    penalty_decision_gov = models.CharField(max_length=50)
    penalty_decision_date = models.DataTimeField()
    detail = models.CharField(max_length=30)
    penalty_register_date = models.DataTimeField()
    enter_name = models.CharField(max_length=50)
    creidit_code = models.CharField(max_length=20)
    corporation  = models.CharField(max_length=30)
    penalty_publicity_time  = models.DataTimeField()
    enter_id  = models.CharField(max_length=30)
    bas_id  = models.IntField()


class IndustryCommerceBranch(models.Model):
    """工商-分支机构
    """

    enter_code = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=30)
    register_gov = models.CharField(max_length=50)
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntField()


class IndustryCommerceChange(models.Model):
    """工商-变更
    """

    modify_item = models.CharField(max_length=30)
    modify_before = models.CharField(max_length=50)
    modify_after = models.CharField(max_length=50)
    modify_date = models.DataTimeField()
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntField()


class IndustryCommerceCheck(models.Model):
    """工商-抽查检查
    """

    check_gov = models.CharField(max_length=50)
    check_type = models.CharField(max_length=20)
    check_date = models.DataTimeField()
    check_result = models.CharField(max_length=50)
    check_comment = models.CharField(max_length=50)
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntField()


class IndustryCommerceClear(models.Model):
    """工商-清算
    """

    person_in_charge = models.CharField(max_length=30)
    persons = models.CharField(max_length=100)
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntField()


class IndustryCommerceDetailGuarantee(models.Model):
    """工商-动产抵押-详情-动产抵押
    """

    register_code = models.CharField(max_length=20)
    sharechange_register_date = models.DataTimeField()
    register_gov = models.CharField(max_length=50)
    register_id = models.CharField(max_length=20)
    ind_id = models.IntField()


class IndustryCommerceException(models.Model):
    """工商-经营异常
    """

    list_on_reason = models.CharField(max_length=100)
    list_on_date = models.DataTimeField()
    list_out_reason = models.CharField(max_length=100)
    list_out_date = models.DataTimeField()
    list_gov = models.CharField(max_length=50)
    list_on_gov = models.CharField(max_length=50)
    list_out_gov = models.CharField(max_length=50)
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntField()


class IndustryCommerceIllegal(models.Model):
    """工商-严重违法
    """

    list_on_reason = models.CharField(max_length=100)
    list_on_date = models.DataTimeField()
    list_out_reason = models.CharField(max_length=100)
    list_out_date = models.DataTimeField(max_length=100)
    decision_gov = models.CharField(max_length=30)
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntField()


class IndustryCommerceMainperson(models.Model):
    """工商-主要人员
    """

    name = models.CharField(max_length=30)
    position = models.CharField(max_length=20)
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntField(max_length=100)


class IndustryCommerceMortgage(models.Model):
    """工商-动产抵押登记
    """
    
    register_num = models.CharField(max_length=20)
    sharechange_register_date = models.DateTimeField()
    register_gov = models.CharField(max_length=50)
    guarantee_debt_amount = models.FloatField()
    status = models.CharField(max_length=20)
    publicity_time = models.DateTimeField()
    details = models.TextField()
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntegerField()
