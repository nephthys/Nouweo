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

from django.db.models import Count
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext, defaultfilters
from django.utils.translation import ugettext as _
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from models import PostType, News, Category, Picture, Version, NewsForm

def homepage(request, page=0):
    status_allowed = [3]
    if request.user.is_authenticated():
        status_allowed = [1, 3]
    
    posts_list = PostType.objects.filter(status__in=status_allowed) \
        .order_by('-updated_at').select_related('category', \
        'news__last_version', 'news__last_version__author').select_subclasses()
    
    for post in posts_list:
        print post.parent
        # print post.__dict__
    
    return render_to_response('posts/homepage.html', {'posts_list': \
        posts_list}, context_instance=RequestContext(request))

def view_post(request, cat, slug, revision=0):
    try:
        post = PostType.objects.filter(slug=slug).select_related('category', \
            'news__last_version').select_subclasses()[0]
    except IndexError, PostType.DoesNotExist:
        raise Http404

    return render_to_response('posts/view_post.html', {'post': post}, \
            context_instance=RequestContext(request))

@login_required
def add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data['content_news']
            
            news = form.save(commit=False)
            news.is_short = form.cleaned_data['is_short']
            news.last_content = content
            news.ip = request.META['REMOTE_ADDR']
            news.save()
            
            version = Version(news=news, author=request.user, \
                ip=request.META['REMOTE_ADDR'], content=content, \
                is_minor=form.cleaned_data['is_minor'], \
                nb_chars=len(form.cleaned_data['content_news']))
            version.save()

            news.last_version = version
            news.save()
            
            return HttpResponseRedirect(news.get_absolute_url())
    else:
        initial = {'reason': _('First version')}
        form = NewsForm(initial=initial)
    
    return render_to_response('posts/add_news.html', {'form': form}, \
            context_instance=RequestContext(request))