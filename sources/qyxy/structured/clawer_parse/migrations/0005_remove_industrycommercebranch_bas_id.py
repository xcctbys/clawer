# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0004_auto_20160125_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='industrycommercebranch',
            name='bas_id',
        ),
    ]
