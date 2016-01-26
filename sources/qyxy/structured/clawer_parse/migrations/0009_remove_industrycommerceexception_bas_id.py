# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0008_remove_industrycommerceclear_bas_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='industrycommerceexception',
            name='bas_id',
        ),
    ]
