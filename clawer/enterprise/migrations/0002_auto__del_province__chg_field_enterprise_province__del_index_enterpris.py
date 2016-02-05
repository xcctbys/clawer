# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Province'
        db.delete_table('enterprise_province')


        # Renaming column for 'Enterprise.province' to match new field type.
        db.rename_column('enterprise_enterprise', 'province_id', 'province')
        # Changing field 'Enterprise.province'
        db.alter_column('enterprise_enterprise', 'province', self.gf('django.db.models.fields.CharField')(max_length=128))
        # Removing index on 'Enterprise', fields ['province']
        db.delete_index('enterprise_enterprise', ['province_id'])


    def backwards(self, orm):
        # Adding index on 'Enterprise', fields ['province']
        db.create_index('enterprise_enterprise', ['province_id'])

        # Adding model 'Province'
        db.create_table('enterprise_province', (
            ('label', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('add_datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('enterprise', ['Province'])


        # Renaming column for 'Enterprise.province' to match new field type.
        db.rename_column('enterprise_enterprise', 'province', 'province_id')
        # Changing field 'Enterprise.province'
        db.alter_column('enterprise_enterprise', 'province_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['enterprise.Province']))

    models = {
        'enterprise.enterprise': {
            'Meta': {'object_name': 'Enterprise'},
            'add_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'register_no': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['enterprise']