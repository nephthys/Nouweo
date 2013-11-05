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
from django.contrib.auth import get_user_model
from posts.models import PostType, News, Picture, Version


def karma_rating_post(instance):
    """
    Performs different actions following a vote on a post.

    Pending posts (post.status = 2) : A number of positive votes are required
    to publish a post. Otherwise, it is rejected after several negative votes.
    """
    pos_votes_to_publish = getattr(settings,
                                   'NOUWEO_POS_VOTES_TO_PUBLISH_POST', 30)
    neg_votes_to_publish = getattr(settings,
                                   'NOUWEO_NEG_VOTES_TO_PUBLISH_POST', -30)
    post = instance.content_object

    if post.status == 2:
        if post.rating_sum == pos_votes_to_publish:
            post.status = 3
            post.save()


def karma_rating_comment_published(instance):
    """
    Reward / punish a constructive / useless published comment due to
    a positive / negative vote of a user.
    """
    user = get_user_model().objects.get(pk=instance.user.id)

    object_id = instance.content_object.id
    post = instance.content_object.content_object

    if post.status == 3:
        if int(instance.value) > 0:
            action_id = 'post_positive_comment'
        else:
            action_id = 'post_negative_comment'

        user.change_karma(action_id, content_type=instance.content_type,
                          object_id=object_id)


def karma_post_published(post_id):
    """
    Reward users following the publication of news, brief, picture or video.
    For news, the minor contributions earn less reputation points.
    """
    try:
        post = PostType.objects.filter(id=post_id).select_subclasses()[0]

        if isinstance(post, News):
            query_set = Version.objects.filter(news=post, is_minor=False)
            query_set.query.group_by = ['author_id']

            for rev in query_set:
                user = get_user_model().objects.get(pk=rev.author.id)
                user.change_karma('news_published', obj=post.parent)

    except IndexError, PostType.DoesNotExist:
        pass
