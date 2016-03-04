# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Enterprise'
        db.create_table('enterprise_enterprise', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('province', self.gf('django.db.models.fields.IntegerField')(max_length=128)),
            ('register_no', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('add_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('enterprise', ['Enterprise'])


    def backwards(self, orm):
        # Deleting model 'Enterprise'
        db.delete_table('enterprise_enterprise')


    models = {
        'enterprise.enterprise': {
            'Meta': {'object_name': 'Enterprise'},
            'add_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'province': ('django.db.models.fields.IntegerField', [], {'max_length': '128'}),
            'register_no': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['enterprise']