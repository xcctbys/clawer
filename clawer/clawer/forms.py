#encoding=utf-8

from django import forms

from clawer.models import Clawer


class UpdateClawerTaskGenerator(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    code_file = forms.FileField()
    cron = forms.CharField(max_length=64)
    
    
class UpdateClawerAnalysis(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    code_file = forms.FileField()
    

class AddClawerTask(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    uri = forms.CharField(max_length=4096)
    cookie = forms.CharField(max_length=4096, required=False)
    

class UpdateClawerSetting(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    dispatch = forms.IntegerField()
    analysis = forms.IntegerField()
    proxy = forms.CharField(max_length=4096, required=False)
    
