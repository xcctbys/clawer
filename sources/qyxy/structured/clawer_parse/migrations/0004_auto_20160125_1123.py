# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clawer_parse', '0003_remove_entersharechange_bas_id'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='industrycommerceadministrativepenalty',
            table='industry_commerce_administrative_penalty',
        ),
    ]
