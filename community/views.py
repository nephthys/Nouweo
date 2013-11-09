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

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseRedirect, Http404
from posts.models import PostType, Idea
from models import ThreadedComment


def view_user_profile(request, id):
    try:
        user = get_user_model().objects.get(pk=id, is_active=True)
        return render(request, 'user_profile.html', {'user': user})
    except ObjectDoesNotExist:
        pass


@login_required
def add_vote(request, model, id, direction):
    user = request.user
    value = 1 if direction == 'up' else -1
    ip = request.META['REMOTE_ADDR']
    vote = {}
    permalink = None

    if model == 'post':
        obj = get_object_or_404(PostType, pk=id)
        if obj.status in [2, 3]:
            vote = obj.rating.add(user, value, ip, obj.status)
    elif model == 'idea':
        obj = get_object_or_404(Idea, pk=id)
        if obj.status == 1:
            vote = obj.rating.add(user, value, ip, obj.status)

    if request.is_ajax():
        import json
        return HttpResponse(json.dumps(vote), mimetype='application/json')
    else:
        permalink = obj.get_absolute_url()
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
