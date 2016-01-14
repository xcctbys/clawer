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

    `penalty_decision_num` = [value-1], 
    `illegal_type` = [value-2], 
    `penalty_content` = [value-3], 
    `penalty_decision_gov` = [value-4], 
    `penalty_decision_date` = [value-5], 
    `detail` = [value-6], 
    `penalty_register_date` = [value-7], 
    `enter_name` = [value-8], 
    `creidit_code` = [value-9], 
    `corporation` = [value-10], 
    `penalty_publicity_time` = [value-11], 
    `enter_id` = [value-12], 
    `id` = [value-13], 
    `bas_id` = [value-14] 

class industry_commerce_branch(models.Model):
 
    `enter_code` = [value-1], 
    `branch_name` = [value-2], 
    `register_gov` = [value-3], 
    `enter_id` = [value-4], 
    `id` = [value-5], 
    `bas_id` = [value-6] 

class  industry_commerce_change(models.Model):


    `modify_item` = [value-1], 
    `modify_before` = [value-2], 
    `modify_after` = [value-3], 
    `modify_date` = [value-4], 
    `enter_id` = [value-5], 
    `id` = [value-6], 
    `bas_id` = [value-7] 


class  industry_commerce_check(models.Model):


    `check_gov` = [value-1], 
    `check_type` = [value-2], 
    `check_date` = [value-3], 
    `check_result` = [value-4], 
    `check_comment` = [value-5], 
    `enter_id` = [value-6], 
    `id` = [value-7], 
    `bas_id` = [value-8] 



class  industry_commerce_clear(models.Model):

    `person_in_charge` = [value-1], 
    `persons` = [value-2], 
    `enter_id` = [value-3], 
    `id` = [value-4], 
    `bas_id` = [value-5] 



class  industry_commerce_detail_guarantee(models.Model):

    `register_code` = [value-1], 
    `sharechange_register_date` = [value-2], 
    `register_gov` = [value-3], 
    `register_id` = [value-4], 
    `id` = [value-5], 
    `ind_id` = [value-6] 


class  industry_commerce_exception(models.Model):
 
    `list_on_reason` = [value-1], 
    `list_on_date` = [value-2], 
    `list_out_reason` = [value-3], 
    `list_out_date` = [value-4], 
    `list_gov` = [value-5], 
    `list_on_gov` = [value-6], 
    `list_out_gov` = [value-7], 
    `enter_id` = [value-8], 
    `id` = [value-9], 
    `bas_id` = [value-10] 



class  industry_commerce_illegal(models.Model):   


    `list_on_reason` = [value-1], 
    `list_on_date` = [value-2], 
    `list_out_reason` = [value-3], 
    `list_out_date` = [value-4], 
    `decision_gov` = [value-5], 
    `enter_id` = [value-6], 
    `id` = [value-7], 
    `bas_id` = [value-8] 

class  industry_commerce_mainperson(models.Model): 


    `name` = [value-1], 
    `position` = [value-2], 
    `enter_id` = [value-3], 
    `id` = [value-4], 
    `bas_id` = [value-5] 



