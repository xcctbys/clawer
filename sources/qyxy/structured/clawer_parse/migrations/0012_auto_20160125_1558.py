# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0011_auto_20160125_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industrycommerceadministrativepenalty',
            name='penalty_decision_num',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
