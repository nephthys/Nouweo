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
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext, defaultfilters
from django.utils.translation import ugettext as _
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseRedirect
from models import PostType, News, Picture, Category, Version, Idea, \
    IdeaForm, NewsForm
from mezzanine.generic.models import ThreadedComment, Rating


def homepage(request, page=0):
    status_allowed = [3]
    if request.user.is_authenticated():
        status_allowed = [1, 3]

    posts_list = PostType.objects.filter(status__in=status_allowed) \
                         .order_by('-updated_at') \
                         .select_related('category', 'news__last_version',
                                         'news__last_version__author') \
                         .select_subclasses()

    for post in posts_list:
        print post.parent
        # print post.__dict__

    return render(request, 'posts/homepage.html', {'posts_list': posts_list})


@login_required
def view_posts_draft(request):
    """
    Displays a list of ideas, the form to add / update ideas, and writing posts
    """
    idea = None
    idea_id = request.GET.get('idea_id', 0)

    if idea_id:
        idea = get_object_or_404(Idea, pk=idea_id)

    if request.method == 'POST':
        form = IdeaForm(request.POST, instance=idea, user=request.user,
                        ip=request.META['REMOTE_ADDR'])
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('posts_draft'))
    else:
        form = IdeaForm(instance=idea)

    ideas_list = Idea.objects.select_related().filter(status=1) \
        .order_by('-rating_average')

    news_list = News.objects.filter(status=1) \
                    .order_by('-updated_at') \
                    .select_related('category', 'last_version',
                                    'last_version__author') \
                    .prefetch_related('versions', 'versions__author')

    for news in news_list:
        for rev in news.versions.all():
            print rev.id

    last_revisions = Version.objects.select_related().filter(news__status=1) \
        .order_by('-created_at')[:10]

    return render(request, 'posts/posts_draft.html', {
        'ideas_list': ideas_list, 'news_list': news_list,
        'last_revisions': last_revisions, 'form': form, 'idea_id': idea_id
    })


@login_required
def view_posts_pending(request):
    posts_list = PostType.objects.filter(status=2) \
                         .order_by('-updated_at') \
                         .select_related('category', 'news__last_version',
                                         'news__last_version__author') \
                         .select_subclasses()

    ctype = ContentType.objects.get_for_model(PostType)
    best_voters = Rating.objects.filter(content_type=ctype) \
        .annotate(num_votes=Count('user')).order_by('-num_votes')[:10]

    last_comments = ThreadedComment.objects.filter(content_type=ctype) \
        .select_related().order_by('-submit_date')[:10]

    return render(request, 'posts/posts_pending.html', {
        'posts_list': posts_list, 'best_voters': best_voters,
        'last_comments': last_comments
    })


def view_post(request, cat, slug, revision=0):
    try:
        post = PostType.objects.filter(slug=slug) \
                       .select_related('category', 'news__last_version') \
                       .select_subclasses()[0]
    except IndexError, PostType.DoesNotExist:
        raise Http404

    return render(request, 'posts/view_post.html', {'post': post})


def view_revisions(request, cat, slug):
    news = get_object_or_404(News, slug=slug)
    revisions = Version.objects.select_related().filter(news=news) \
        .order_by('-created_at')

    diff = ''
    nb_revisions = revisions.count()

    old_id = request.GET.get('old', None)
    new_id = request.GET.get('new', None)

    if old_id is not None and new_id is not None:
        from htmldiff import render_html_diff

        old_rev = Version.objects.get(id=old_id).content_html
        new_rev = Version.objects.get(id=new_id).content_html

        diff = render_html_diff(old_rev, new_rev)

    return render(request, 'posts/view_post_revisions.html', {
        'post': news, 'post_revisions': revisions,
        'nb_revisions': nb_revisions, 'diff': diff
    })


@login_required
def select_revision(request, cat, slug, revision):
    news = get_object_or_404(News, slug=slug)
    rev = get_object_or_404(Version, pk=revision)

    if int(news.last_version.id) != int(rev.id):
        news.last_content = rev.content
        news.last_version = rev
        news.save()

    return HttpResponseRedirect(reverse('post_revisions',
                                kwargs={'cat': cat, 'slug': slug}))


@login_required
def delete_revision(request, cat, slug, revision):
    news = get_object_or_404(News, slug=slug)
    rev = get_object_or_404(Version, pk=revision)

    if news.nb_versions > 1:
        if int(news.last_version.id) == int(rev.id):
            prev_rev = Version.objects.filter(news=news) \
                              .filter(id__lt=rev.id).order_by('-created_at')[0]
            news.last_content = prev_rev.content
            news.last_version = prev_rev

        rev.delete()
        news.nb_versions -= 1
        news.save()

    return HttpResponseRedirect(reverse('post_revisions',
                                        kwargs={'cat': cat, 'slug': slug}))


@login_required
def post_propose(request, post_id):
    post = get_object_or_404(PostType, pk=post_id)
    if post.status == 1:
        post.status = 2
        post.save()
    return HttpResponseRedirect(reverse('posts_draft'))


@login_required
def add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, user=request.user,
                        ip=request.META['REMOTE_ADDR'])
        if form.is_valid():
            news = form.save()
            return HttpResponseRedirect(news.get_absolute_url())
    else:
        initial = {'reason': _('First version')}
        form = NewsForm(initial=initial)

    return render(request, 'posts/add_news.html', {'form': form})
