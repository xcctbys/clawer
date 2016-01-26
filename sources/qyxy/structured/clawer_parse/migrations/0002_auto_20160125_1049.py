# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enterannualreport',
            name='bas_id',
        ),
        migrations.RemoveField(
            model_name='enterannualreport',
            name='primary',
        ),
    ]
