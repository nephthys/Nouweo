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

from collections import defaultdict
from django import template

from ..utils import order_by_score

register = template.Library()


@register.simple_tag(takes_context=True)
def widget_poll(context, poll_id):
    return 'hello poll %s' % poll_id


@register.simple_tag(takes_context=True)
def order_comments_by_score_for(context, obj):
    """
    Preloads threaded comments in the same way Mezzanine initially does,
    but here we order them by score.

    Source : https://github.com/stephenmcd/drum/blob/master/main/templatetags/drum_tags.py
    """
    comments = defaultdict(list)
    qs = obj.comments.visible().select_related("user", "user__profile")
    for comment in order_by_score(qs, ("rating_sum",), "submit_date"):
        comments[comment.replied_to_id].append(comment)
    context["all_comments"] = comments
    return ""
