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
