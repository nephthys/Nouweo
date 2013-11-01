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

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    karma = models.IntegerField(default=0)
    thumbs_up = models.IntegerField(default=0)
    thumbs_down = models.IntegerField(default=0)
    thumbs_ratio = models.IntegerField(default=0)
    location = models.CharField(max_length=150, null=True, blank=True)
    
    subscribe_newsletter = models.BooleanField(default=False)

    objects = UserManager()

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
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
