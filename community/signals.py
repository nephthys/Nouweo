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

from django.contrib.auth import get_user_model
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from mezzanine.generic.models import Rating, ThreadedComment

from posts.models import PostType, News, Picture
from models import KarmaAction, KarmaChange


@receiver(post_save, sender=Rating)
def new_rating(sender, instance, signal, created, **kwargs):
    if isinstance(instance.content_object, ThreadedComment) \
    and isinstance(instance.content_object.content_object, PostType):

        from community.karma import karma_rating_comment_published
        karma_rating_comment_published(instance)

    elif isinstance(instance.content_object, PostType):

        from community.karma import karma_rating_post
        karma_rating_post(instance)

