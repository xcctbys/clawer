#encoding=utf-8

from django import forms

from clawer.models import Clawer


class UpdateClawerTaskGenerator(forms.Form):
    clawer = forms.ModelChoiceField(queryset=Clawer.objects)
    code_file = forms.FileField()