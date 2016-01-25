# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0002_auto_20160125_1049'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entersharechange',
            name='bas_id',
        ),
    ]
