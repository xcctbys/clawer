# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0005_remove_industrycommercebranch_bas_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='industrycommercechange',
            name='bas_id',
        ),
    ]
