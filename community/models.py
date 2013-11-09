#!/usr/bin/env python
#-*- encoding: utf-8 -*-
"""
Copyright (c) 2013 Camille "nephthys" Bouiller <camille@nouweo.com>

Nouweo is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager, Permission
from django.contrib.comments.forms import CommentSecurityForm
from django.contrib.comments.models import BaseCommentAbstractModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from fields import RatingField
from managers import VoteManager

import datetime


class User(AbstractUser):
    karma = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    location = models.CharField(max_length=150, null=True, blank=True)

    subscribe_newsletter = models.BooleanField(default=False)

    objects = UserManager()

    def has_privilege(self, privilege_id, **kwargs):
        try:
            privilege = KarmaPrivilege.objects.get(permission__codename=
                                                   privilege_id)
            if self.karma >= privilege.minimum_points:
                return True
        except KarmaPrivilege.DoesNotExist:
            pass
        return False

    def change_karma(self, action_id, **kwargs):
        try:
            action = KarmaAction.objects.get(identifier=action_id)

            content_type = kwargs.pop('content_type', None)
            object_id = kwargs.pop('object_id', None)

            if content_type is None and object_id is None:
                obj = kwargs.pop('obj', None)

                content_type = ContentType.objects.get_for_model(obj)
                object_id = obj.pk

            karma = KarmaChange.objects.filter(user=self,
                                               content_type=content_type,
                                               object_id=object_id)

            if karma.count() > 0:
                change = karma[0]
                old_points = change.points
                change.points = action.points
                change.save()

                self.karma += (action.points - old_points)
                self.save()
            else:
                change = KarmaChange()
                change.action = action
                change.user = self
                change.points = action.points

                if content_type is not None and object_id is not None:
                    change.content_type = content_type
                    change.object_id = object_id

                change.save()

                self.karma += action.points
                self.save()

            return change
        except KarmaAction.DoesNotExist:
            pass


class KarmaAction(models.Model):
    name = models.CharField(max_length=150)
    identifier = models.CharField(unique=True, max_length=150)
    points = models.SmallIntegerField()


class KarmaChange(models.Model):
    action = models.ForeignKey(KarmaAction)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(auto_now_add=True)
    points = models.SmallIntegerField()
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_pk = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_pk')


class KarmaPrivilege(models.Model):
    permission = models.ForeignKey(Permission)
    minimum_points = models.IntegerField()


class Vote(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_pk = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_pk')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(auto_now_add=True)
    value = models.SmallIntegerField()
    status = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    ip = models.IPAddressField(_('IP address'))

    objects = VoteManager()


class ThreadedComment(BaseCommentAbstractModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment = models.TextField()
    comment_html = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)
    replied_to = models.ForeignKey('self', null=True, editable=False,
                                   related_name='comments')
    ip_address = models.IPAddressField(_('IP address'))
    rating = RatingField()

    def get_absolute_url(self):
        url = self.content_object.get_absolute_url()
        return '%s#comment-%s' % (url, self.id)


class ThreadedCommentForm(CommentSecurityForm):
    comment = forms.CharField(label=_('Comment'), widget=forms.Textarea)
    replied_to = forms.CharField(widget=forms.HiddenInput, required=False)

    def get_comment_object(self):
        if not self.is_valid():
            raise ValueError('get_comment_object may only be called on valid forms')

        CommentModel = self.get_comment_model()
        new = CommentModel(**self.get_comment_create_data())
        return new

    def get_comment_model(self):
        return ThreadedComment

    def get_comment_create_data(self):
        import markdown

        data = dict(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk    = force_text(self.target_object._get_pk_val()),
            comment      = self.cleaned_data['comment'],
            comment_html = markdown.markdown(self.cleaned_data['comment']),
            created_at   = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            # is_public    = True,
            # is_removed   = False,
        )

        if self.cleaned_data.get('replied_to'):
            data['replied_to_id'] = self.cleaned_data.get('replied_to')

        return data


import signals
