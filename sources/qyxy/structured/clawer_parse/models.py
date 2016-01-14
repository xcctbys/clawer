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


class industry_commerce_administrative_penalty(models.Model):

    penalty_decision_num
    illegal_type
    penalty_content
    penalty_decision_gov
    penalty_decision_date
    detail
    penalty_register_date
    enter_name
    creidit_code
    corporation
    penalty_publicity_time
    enter_id
    bas_id


class industry_commerce_branch(models.Model):

    enter_code
    branch_name
    register_gov
    enter_id
    bas_id


class  industry_commerce_change(models.Model):


    modify_item
    modify_before
    modify_after
    modify_date
    enter_id
    bas_id


class  industry_commerce_check(models.Model):


    check_gov
    check_type
    check_date
    check_result
    check_comment
    enter_id
    bas_id


class  industry_commerce_clear(models.Model):

    person_in_charge
    persons
    enter_id
    bas_id


class  industry_commerce_detail_guarantee(models.Model):

    register_code
    sharechange_register_date
    register_gov
    register_id
    ind_id


class  industry_commerce_exception(models.Model):

    list_on_reason
    list_on_date
    list_out_reason
    list_out_date
    list_gov
    list_on_gov
    list_out_gov
    enter_id
    bas_id


class  industry_commerce_illegal(models.Model):


    list_on_reason
    list_on_date
    list_out_reason
    list_out_date
    decision_gov
    enter_id
    bas_id


class  industry_commerce_mainperson(models.Model):

    name
    position
    enter_id
    bas_id


class industry_commerce_mortgage(models.Model):
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


class industry_commerce_mortgage_detail_change(models.Model):
    """工商-抵押-详情-变更
    """

    modify_date = models.DateTimeField()
    modify_content = models.TextField()
    register_id = models.CharField(max_length=20)
    ind_id = models.IntegerField()


class industry_commerce_mortgage_detail_guarantee(models.Model):
    """工商-抵押-详情-抵押权人
    """

    check_type = models.CharField(max_length=20)
    amount = models.FloatField()
    guarantee_scope = models.CharField(max_length=100)
    debtor_duration = models.CharField(max_length=20)
    comment = models.CharField(max_length=100)
    register_id = models.CharField(max_length=20)
    ind_id = models.IntegerField()


class industry_commerce_mortgage_guaranty(models.Model):
    """工商-抵押-详情-抵押物
    """

    name = models.CharField(max_length=30)
    ownership = models.CharField(max_length=30)
    details = models.TextField()
    coments = models.CharField(max_length=100)
    register_id = models.CharField(max_length=20)
    ind_id = models.IntegerField()


class industry_commerce_revoke(models.Model):
    """工商-撤销
    """

    revoke_item = models.CharField(max_length=30)
    content_before_revoke = models.CharField(max_length=50)
    content_after_revoke = models.CharField(max_length=50)
    revoke_date = models.DateTimeField()
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntegerField()

class industry_commerce_shareholders(models.Model):
    """工商-股东
    """

    shareholder_type = models.CharField(max_length=20)
    shareholder_name = models.CharField(max_length=30)
    certificate_type = models.CharField(max_length=20)
    certificate_number = models.CharField(max_length=20)
    subscription_amount = models.FloatField()
    paid_amount = models.FloatField()
    subscription_type = models.CharField(max_length=30)
    subscription_date = models.DateTimeField()
    subscription_money_amount = models.FloatField()
    paid_type = models.CharField(max_length=20)
    paid_money_amount = models.FloatField()
    paid_date = models.DateTimeField()
    enter_id = models.CharField(max_length=20)
    bas_id = models.IntegerField()


class industry_commerce_sharepledge(models.Model):
    """
    """

    register_num = models.CharField(max_length=20)
    pledgor = models.CharField(max_length=30)
    pledgor_certificate_code = models.CharField(max_length=20)
    share_pledge_num = models.FloatField()
    mortgagee = models.CharField(max_length=30)
    mortgagee_certificate_code = models.CharField(max_length=20)
    sharechange_register_date = models.DateTimeField()
    status = models.CharField(max_length=20)
    change_detail = models.CharField(max_length=100)
    publicity_time = models.DateTimeField()
    modify_date = models.DateTimeField()
    modify_content = models.TextField()
    register_id = models.CharField(max_length=20)
    bas_id = models.IntegerField()


class industry_mortgage_detail_mortgagee(models.Model):
    """工商-抵押-详情-抵押权人
    """

    mortgagee_name = models.CharField(max_length=30)
    mortgagee_certificate_type = models.CharField(max_length=20)
    pledgor_certificate_code = models.CharField(max_length=20)
    register_id = models.CharField(max_length=20)
    ind_id = models.IntegerField()
