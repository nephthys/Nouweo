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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from mezzanine.generic.models import ThreadedComment
from posts.models import PostType, News, Picture
from models import Vote, ThreadedComment

'''
@receiver(post_save, sender=Rating)
def new_rating(sender, instance, signal, created, **kwargs):
    if isinstance(instance.content_object, ThreadedComment) \
    and isinstance(instance.content_object.content_object, PostType):

        from community.karma import karma_rating_comment_published
        karma_rating_comment_published(instance)

    elif isinstance(instance.content_object, PostType):

        from community.karma import karma_rating_post
        karma_rating_post(instance)
'''

@receiver(post_save, sender=Vote)
@receiver(post_delete, sender=Vote)
def count_user_votes(sender, instance, signal, created, **kwargs):
    try:
        user = get_user_model().objects.get(pk=instance.user.id)
        user.likes = Vote.objects.filter(user=user, value__gt=0).count()
        user.dislikes = Vote.objects.filter(user=user, value__lt=0).count()
        user.save()
    except ObjectDoesNotExist:
        pass


@receiver(post_save, sender=ThreadedComment)
@receiver(post_delete, sender=ThreadedComment)
def count_user_comments(sender, instance, signal, created, **kwargs):
    try:
        user = get_user_model().objects.get(pk=instance.user.id)
        user.comments = ThreadedComment.objects.filter(user=user).count()
        user.save()
    except ObjectDoesNotExist:
        pass
