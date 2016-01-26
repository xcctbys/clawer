# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0014_auto_20160125_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enteradministrativepenalty',
            name='penalty_decision_num',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
