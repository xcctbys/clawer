# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0009_remove_industrycommerceexception_bas_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='industrycommerceshareholders',
            name='bas_id',
        ),
    ]
