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

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseRedirect, Http404
from posts.models import PostType, Idea
from models import ThreadedComment

@login_required
def add_vote(request, model, id, direction):
    user = request.user
    value = 1 if direction == 'up' else -1
    ip = request.META['REMOTE_ADDR']
    vote = {}
    permalink = None

    if model == 'post':
        post = get_object_or_404(PostType, pk=id)
        permalink = post.get_absolute_url()
        if post.status in [1, 3]:
            vote = post.rating.add(user, value, ip, post.status)
    elif model == 'idea':
        idea = get_object_or_404(Idea, pk=id)
        permalink = idea.get_absolute_url()
        if idea.status == 1:
            vote = idea.rating.add(user, value, ip, idea.status)

    if request.is_ajax():
        import json
        return HttpResponse(json.dumps(vote), mimetype='application/json')
    else:
        referer = request.META.get('HTTP_REFERER', None)
        return HttpResponseRedirect(referer if referer else permalink)


def comment_posted(request):
    comment_id = request.GET.get('c', None)
    if comment_id:
        comment = get_object_or_404(ThreadedComment, pk=comment_id)
        permalink_obj = comment.content_object.get_absolute_url()
        return HttpResponseRedirect('%s#c%d' % (permalink_obj, int(comment_id)))
    else:
        raise Http404
