# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Enterprise.province'
        db.alter_column('enterprise_enterprise', 'province', self.gf('django.db.models.fields.IntegerField')(max_length=128))

    def backwards(self, orm):

        # Changing field 'Enterprise.province'
        db.alter_column('enterprise_enterprise', 'province', self.gf('django.db.models.fields.CharField')(max_length=128))

    models = {
        'enterprise.enterprise': {
            'Meta': {'object_name': 'Enterprise'},
            'add_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'province': ('django.db.models.fields.IntegerField', [], {'max_length': '128'}),
            'register_no': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['enterprise']