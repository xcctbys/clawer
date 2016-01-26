# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0006_remove_industrycommercechange_bas_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='industrycommercecheck',
            name='bas_id',
        ),
    ]
