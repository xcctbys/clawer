# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0012_auto_20160125_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enteradministrativepenalty',
            name='illegal_type',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='industrycommerceadministrativepenalty',
            name='illegal_type',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='otheradministrativepenalty',
            name='illegal_type',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
