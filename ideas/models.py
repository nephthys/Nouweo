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
from django.db import models
from django.utils.translation import ugettext as _
from posts.models import PostType
from community.fields import RatingField
from django_permanent.models import PermanentModel

class Idea(PermanentModel):
    CHOICE_STATUS = (
        (1, _('Refused')),
        (2, _('Pending')),
        (3, _('Completed')),
    )
    title = models.CharField(_('title'), max_length=150)
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created date'), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='created_by',
                                   null=True, blank=True)
    updated_at = models.DateTimeField(_('last update'), null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='updated_by',
                                   null=True, blank=True)
    completed_at = models.DateTimeField(_('completed date'), null=True,
                                        blank=True)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='completed_by',
                                     null=True, blank=True)
    completed_post = models.ForeignKey(PostType, null=True, blank=True)
    status = models.PositiveSmallIntegerField(default=2, choices=CHOICE_STATUS)
    ip = models.IPAddressField(_('IP address'))
    rating = RatingField(count_status='status')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '%s?idea_id=%d' % (reverse('posts_draft'), self.id)

