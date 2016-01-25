# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0013_auto_20160125_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industrycommerceadministrativepenalty',
            name='detail',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='judicialshareholderchange',
            name='detail',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='otheradministrativepenalty',
            name='detail',
            field=models.TextField(null=True, blank=True),
        ),
    ]
