#!/usr/bin/env python
#-*- encoding: utf-8 -*-
'''
Copyright (c) 2013 Camille 'nephthys' Bouiller <camille@nouweo.com>

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
'''

from collections import defaultdict
from django import template

from community.models import ThreadedComment
from ..utils import order_by_score

register = template.Library()


@register.simple_tag(takes_context=True)
def widget_poll(context, poll_id):
    return 'hello poll %s' % poll_id


@register.inclusion_tag('includes/comments.html', takes_context=True)
def comments_for(context, obj):
    context['object_for_comments'] = obj
    return context


@register.simple_tag(takes_context=True)
def order_comments_by_score_for(context, obj):
    '''
    Preloads threaded comments in the same way Mezzanine initially does,
    but here we order them by score.

    Source : https://github.com/stephenmcd/drum/blob/master/main/templatetags/drum_tags.py
    '''
    comments = defaultdict(list)
    # qs = obj.comments.visible().select_related('user')
    qs = obj.comments.select_related('user')
    for comment in order_by_score(qs, ('rating_sum',), 'created_at'):
        comments[comment.replied_to_id].append(comment)
    context['all_comments'] = comments
    return ''


@register.inclusion_tag('includes/comment.html', takes_context=True)
def comment_thread(context, parent):
    '''
    Return a list of child comments for the given parent, storing all
    comments in a dict in the context when first called, using parents
    as keys for retrieval on subsequent recursive calls from the
    comments template.

    Source : https://github.com/stephenmcd/mezzanine/blob/master/mezzanine/generic/templatetags/comment_tags.py
    '''
    if 'all_comments' not in context:
        comments = defaultdict(list)
        if 'request' in context and context['request'].user.is_staff:
            comments_queryset = parent.comments.all()
        else:
            comments_queryset = parent.comments.visible()
        for comment in comments_queryset.select_related('user'):
            comments[comment.replied_to_id].append(comment)
        context['all_comments'] = comments
    parent_id = parent.id if isinstance(parent, ThreadedComment) else None
    try:
        replied_to = int(context['request'].POST['replied_to'])
    except KeyError:
        replied_to = 0
    context.update({
        'comments_for_thread': context['all_comments'].get(parent_id, []),
        'no_comments': parent_id is None and not context['all_comments'],
        'parent_id': parent_id,
        'replied_to': replied_to,
    })
    return context
