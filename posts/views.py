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
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext, defaultfilters
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseRedirect
from vanilla import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import PostType, News, Picture, Category, Version, NewsForm
from ideas.models import Idea
from ideas.forms import IdeaForm
from community.models import ThreadedComment, Vote
from community.decorators import privileges_required

class PostCRUDView(object):
    model = PostType
    paginate_by = 20

class PostContribView(object):
    model = PostType
    paginate_by = 20

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PostContribView, self).dispatch(*args, **kwargs)

class PostHomepage(PostCRUDView, ListView):
    template_name = 'homepage.html'

    def get_queryset(self):
        status_allowed = [3]
        if self.request.user.is_authenticated():
            status_allowed = [1, 3]
        return PostType.objects.filter(status__in=status_allowed) \
                       .order_by('-updated_at') \
                       .select_related('category', 'news__last_version',
                                       'news__last_version__author') \
                       .select_subclasses()

class PostCreateNews(PostCRUDView, CreateView):
    template_name = 'add_news.html'

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['request'] = self.request
        return NewsForm(data, files, **kwargs)

class PostUpdate(PostCRUDView, UpdateView):
    template_name = 'add_news.html'
    model = News
    form_class = NewsForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PostUpdate, self).dispatch(*args, **kwargs)

    def get_form_class(self):
        return NewsForm

    def get_queryset(self):
        # return News.objects.all()
        return PostType.objects.all() \
                       .select_related('category', 'news__last_version') \
                       .select_subclasses()

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['request'] = self.request
        kwargs['initial'] = self.get_initial()
        form_cls = self.get_form_class()
        return form_cls(data, files, **kwargs)

    def get_initial(self):
        return {
            'is_short': int(self.object.is_short),
            'content_news': self.object.last_content,
            'closed_comments': self.object.closed_comments,
        }

class PostDetailView(object):
    context_object_name = 'post'
    lookup_field = 'slug'

    def get_queryset(self):
        return PostType.objects.all() \
                       .select_related('category', 'news__last_version') \
                       .select_subclasses()


class PostDetail(PostCRUDView, PostDetailView, DetailView):
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)

        revision_id = self.kwargs.get('revision', 0)
        revision = None
        obj = self.get_object()

        if obj.type == 'news' and revision_id != 0:
            revision = get_object_or_404(Version, news=obj, pk=revision_id)

        context['revision'] = revision

        return context

class PostDetailRevisions(PostCRUDView, PostDetailView, DetailView):
    template_name = 'post_detail_revisions.html'

    def compare_revisions(self, old_id, new_id):
        if old_id is None or new_id is None:
            return ''

        from htmldiff import render_html_diff

        old_rev = Version.objects.get(id=old_id).content_html
        new_rev = Version.objects.get(id=new_id).content_html

        return render_html_diff(old_rev, new_rev)

    def get_context_data(self, **kwargs):
        context = super(PostDetailRevisions, self).get_context_data(**kwargs)
        obj = self.get_object()

        old_id = self.request.GET.get('old', None)
        new_id = self.request.GET.get('new', None)

        context['revisions'] = Version.objects.select_related() \
                                      .filter(news=obj).order_by('-created_at')

        context['diff'] = self.compare_revisions(old_id, new_id)

        return context

class PostRevisionView(object):
    model = Version
    lookup_url_kwarg = 'revision'
    news = None

    def get_object(self):
        queryset = self.get_queryset()
        slug = self.kwargs['slug']
        pk = self.kwargs[self.lookup_url_kwarg]
        try:
            self.news = News.objects.get(slug=slug)
            return get_object_or_404(queryset, news=self.news, pk=pk)
        except News.DoesNotExist:
            raise Http404

    def get_success_url(self):
        cat = self.kwargs['cat']
        slug = self.kwargs['slug']
        return reverse('post_revisions', kwargs={'cat': cat, 'slug': slug})


class PostSelectRevision(PostRevisionView, DetailView):
    @method_decorator(privileges_required('posts.delete_version'))
    def dispatch(self, *args, **kwargs):
        return super(PostSelectRevision, self).dispatch(*args, **kwargs)

    def render_to_response(self, context):
        obj = self.get_object()

        if int(self.news.last_version.id) != int(obj.id):
            self.news.last_content = obj.content
            self.news.last_version = obj
            self.news.save()

        return HttpResponse('hello')


class PostDeleteRevision(PostRevisionView, DeleteView):
    template_name = 'post_revision_confirm_delete.html'


class PostDelete(PostCRUDView, DeleteView):
    template_name = 'post_confirm_delete.html'
    success_url = '/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PostDelete, self).dispatch(*args, **kwargs)


class PostDraft(PostContribView, ListView):
    template_name = 'post_draft.html'

    def get_queryset(self):
        return News.objects.filter(status=1) \
                   .order_by('-updated_at', '-created_at') \
                   .select_related('category', 'last_version', 'created_by', \
                                   'updated_by', 'last_version__author') \
                   .prefetch_related('versions', 'versions__author')

    def get_context_data(self, **kwargs):
        context = super(PostDraft, self).get_context_data(**kwargs)

        idea = None
        idea_id = self.request.GET.get('idea_id', 0)
        news_list = self.get_queryset()

        if idea_id:
            idea = get_object_or_404(Idea, pk=idea_id)
            context['idea_id'] = idea_id

        context['form'] = IdeaForm(instance=idea, request=self.request, \
                                   small_display=True)

        context['ideas_list'] = Idea.objects.select_related().filter(status=2) \
            .order_by('-rating_ratio')

        context['last_revisions'] = Version.objects.select_related() \
            .filter(news__status=1).order_by('-created_at')[:10]

        context['last_comments'] = ThreadedComment.objects \
            .filter(object_pk__in=news_list).select_related() \
            .order_by('-created_at')[:10]

        return context


class PostPending(PostContribView, ListView):
    template_name = 'post_pending.html'

    def get_queryset(self):
        return PostType.objects.filter(status=2) \
                       .order_by('-updated_at') \
                       .select_related('category', 'news__last_version',
                                       'news__last_version__author') \
                       .select_subclasses()


    def get_context_data(self, **kwargs):
        context = super(PostPending, self).get_context_data(**kwargs)

        post_ctype = ContentType.objects.get_for_model(PostType)

        context['best_voters'] = Vote.objects.values('user__username') \
            .filter(content_type=post_ctype) \
            .annotate(votes_count=Count('user')).order_by('-votes_count')[:10]

        context['last_comments'] = ThreadedComment.objects \
            .filter(content_type=post_ctype).select_related() \
            .order_by('-created_at')[:10]

        return context


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

    return render(request, 'view_post_revisions.html', {
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


# @privileges_required('posts.delete_version')
def delete_revision(request, cat, slug, revision):
    news = get_object_or_404(News, slug=slug)
    rev = get_object_or_404(Version, pk=revision)

    if news.versions_count > 1:
        if int(news.last_version.id) == int(rev.id):
            prev_rev = Version.objects.filter(news=news) \
                              .filter(id__lt=rev.id).order_by('-created_at')[0]
            news.last_content = prev_rev.content
            news.last_version = prev_rev

        rev.delete()
        news.versions_count -= 1
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
