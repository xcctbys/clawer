# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0010_remove_industrycommerceshareholders_bas_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yearreportwarrandice',
            name='creditor',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
