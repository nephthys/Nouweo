# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'community_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('karma', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('likes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('dislikes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('comments', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('subscribe_newsletter', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'community', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'community_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'community.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'community_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'community.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

        # Adding model 'KarmaAction'
        db.create_table(u'community_karmaaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('identifier', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
            ('points', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'community', ['KarmaAction'])

        # Adding model 'KarmaChange'
        db.create_table(u'community_karmachange', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['community.KarmaAction'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['community.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('points', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_pk', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'community', ['KarmaChange'])

        # Adding model 'KarmaPrivilege'
        db.create_table(u'community_karmaprivilege', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('minimum_points', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'community', ['KarmaPrivilege'])

        # Adding model 'Vote'
        db.create_table(u'community_vote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_pk', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['community.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('value', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, null=True, blank=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal(u'community', ['Vote'])

        # Adding model 'ThreadedComment'
        db.create_table(u'community_threadedcomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content_type_set_for_threadedcomment', to=orm['contenttypes.ContentType'])),
            ('object_pk', self.gf('django.db.models.fields.TextField')()),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['community.User'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('comment_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('replied_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', null=True, to=orm['community.ThreadedComment'])),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('rating_likes', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('rating_dislikes', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('rating_sum', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('rating_ratio', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
        ))
        db.send_create_signal(u'community', ['ThreadedComment'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'community_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'community_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'community_user_user_permissions'))

        # Deleting model 'KarmaAction'
        db.delete_table(u'community_karmaaction')

        # Deleting model 'KarmaChange'
        db.delete_table(u'community_karmachange')

        # Deleting model 'KarmaPrivilege'
        db.delete_table(u'community_karmaprivilege')

        # Deleting model 'Vote'
        db.delete_table(u'community_vote')

        # Deleting model 'ThreadedComment'
        db.delete_table(u'community_threadedcomment')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'community.karmaaction': {
            'Meta': {'object_name': 'KarmaAction'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'points': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'community.karmachange': {
            'Meta': {'object_name': 'KarmaChange'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['community.KarmaAction']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.SmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['community.User']"})
        },
        u'community.karmaprivilege': {
            'Meta': {'object_name': 'KarmaPrivilege'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_points': ('django.db.models.fields.IntegerField', [], {}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Permission']"})
        },
        u'community.threadedcomment': {
            'Meta': {'object_name': 'ThreadedComment'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'comment_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_threadedcomment'", 'to': u"orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'rating_dislikes': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_likes': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_ratio': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'rating_sum': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'replied_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'null': 'True', 'to': u"orm['community.ThreadedComment']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['community.User']"})
        },
        u'community.user': {
            'Meta': {'object_name': 'User'},
            'comments': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'dislikes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'karma': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'likes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'subscribe_newsletter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'community.vote': {
            'Meta': {'object_name': 'Vote'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'object_pk': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['community.User']"}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['community']