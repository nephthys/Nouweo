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

from django import forms
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from model_utils.managers import InheritanceManager

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Div, Row, Field, \
                                MultiField
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, \
                                   InlineCheckboxes, InlineRadios
from community.fields import RatingField, CommentsField

import datetime


class PostType(models.Model):
    CHOICE_STATUS = (
        (0, _('offline')),
        (1, _('writing')),
        (2, _('pending')),
        (3, _('online')),
    )
    title = models.CharField(max_length=150, blank=False, null=False)
    slug = models.SlugField(unique=True, max_length=150, null=True, blank=True)
    category = models.ForeignKey('Category', verbose_name=_('category'))
    created_at = models.DateTimeField(_('created date'), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='user_created',
                                   null=True, blank=True)
    updated_at = models.DateTimeField(_('last update'), null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='user_updated',
                                   null=True, blank=True)
    published_at = models.DateTimeField(_('published date'), null=True,
                                        blank=True)
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='user_published',
                                     null=True, blank=True)
    status = models.PositiveSmallIntegerField(default=1, choices=CHOICE_STATUS)
    closed_comments = models.BooleanField(_('closed comments'), default=False)
    views_count = models.IntegerField(_('number views'), default=0)
    last_content = models.TextField(editable=False, null=True, blank=True)
    last_content_html = models.TextField(editable=False, null=True, blank=True)
    ip = models.IPAddressField(_('IP address'))

    rating = RatingField(count_status='status')
    comments = CommentsField()

    objects = InheritanceManager()

    def get_absolute_url(self):
        return reverse('post_view', kwargs={'cat': self.category.slug,
                                            'slug': self.slug})

    def get_absolute_url_edit(self):
        if self.type is 'news':
            return reverse('edit_news', kwargs={'id': self.id})

    def get_first_author(self):
        return '<a href="%s">%s</a>' % (
            self.created_by.get_absolute_url(),
            self.created_by.username)

    def get_last_author(self):
        if self.updated_by:
            return '<a href="%s">%s</a>' % (
                self.updated_by.get_absolute_url(),
                self.updated_by.username)

    def save(self, *args, **kwargs):
        is_published = False
        status_changed = False

        if not self.slug:
            slug = slugify(self.title)

            while True:
                posts_count = PostType.objects.filter(slug=slug).count()
                if posts_count == 0:
                    break
                slug = '%s-%d' % (slug, (posts_count+1))

            self.slug = slug

        if not self.pk:
            if self.status == 3:
                is_published = True
        else:
            old = PostType.objects.get(pk=self.pk)

            if old.status != self.status:
                status_changed = True

                if self.status == 3:
                    is_published = True

        if self.last_content:
            import markdown
            self.last_content_html = markdown.markdown(self.last_content)

        if not self.published_at and is_published:
            self.published_at = datetime.datetime.now()

        super(PostType, self).save(*args, **kwargs)

        if self.pk and status_changed:
            obj = self
            if hasattr(self, 'parent'):
                obj = self.parent
            output = obj.rating.update_count(commit=False)
            self.__dict__.update(output)
            super(PostType, self).save(*args, **kwargs)

        if self.pk and is_published:
            from community.karma import karma_post_published
            karma_post_published(self.pk)


class News(PostType):
    parent = models.OneToOneField(PostType, parent_link=True)
    last_version = models.ForeignKey('Version', related_name='last_version',
                                     null=True, blank=True,
                                     on_delete=models.SET_NULL)
    versions_count = models.PositiveSmallIntegerField(default=0)
    is_short = models.BooleanField(_('is brief'), default=False)

    @property
    def type(self):
        return 'news'

    def get_short_authors(self):
        list = []
        query_set = Version.objects.filter(is_minor=False)
        query_set.query.group_by = ['author_id']
        for data in query_set:
            author = data.author
            list.append('<a href="%s">%s</a>' % (author.get_absolute_url(),
                                                 author.username))
        return show_first_items(list)

    class Meta:
        verbose_name_plural = "news"


class Version(models.Model):
    news = models.ForeignKey(News, related_name='versions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    number = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now=True)
    content = models.TextField()
    content_html = models.TextField(blank=True)
    reason = models.CharField(max_length=100, blank=True)
    is_minor = models.BooleanField(_('small contribution'), default=False)
    ip = models.IPAddressField(_('IP address'))
    chars_count = models.PositiveSmallIntegerField(default=0)
    chars_diff = models.SmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        import markdown
        self.content_html = markdown.markdown(self.content)

        if self.news.last_version:
            last_version = self.news.last_version
            self.chars_diff = self.chars_count - last_version.chars_count

        try:
            last_number = Version.objects.filter(news=self.news) \
                                         .order_by('-number')[0]
            self.number = last_number.number + 1
        except IndexError, Version.DoesNotExist:
            pass

        super(Version, self).save(*args, **kwargs)


class Picture(PostType):
    parent = models.OneToOneField(PostType, parent_link=True)
    picture = models.ImageField(upload_to='pictures')
    comment = models.TextField()
    comment_html = models.TextField(blank=True)

    @property
    def type(self):
        return 'picture'


class Category(models.Model):
    name = models.CharField(_('name'), max_length=150, blank=False, null=False)
    slug = models.SlugField(_('slug'), unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class NewsForm(ModelForm):
    CHOICE = (
        (0, _('news')),
        (1, _('brief'))
    )

    is_short = forms.ChoiceField(label=_('Type'), required=False, \
                                 choices=CHOICE, widget = forms.RadioSelect)
    content_news = forms.CharField(label=_('Content'),
                                   help_text=_('Write with markdown'),
                                   widget=forms.Textarea(
                                       attrs={'class': 'content_area'}))
    reason = forms.CharField(label=_('Reason'))
    is_minor = forms.BooleanField(label=_('Small contribution'),
                                  required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2 control-label'
        self.helper.field_class = 'col-sm-10'
        self.helper.layout = Layout(
            InlineRadios('is_short'),
            Field('title'),
            Field('category'),
            Field('content_news', rows='3', css_class='input-xlarge'),
            Field('reason'),
            Field('status'),
            Field('is_minor'),
            Field('closed_comments'),
            FormActions(
                Submit('send', _('Send'), css_class='btn-primary')
            )
        )
        self.request = kwargs.pop('request', None)
        super(NewsForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        content = self.cleaned_data.get('content_news', '')
        reason = self.cleaned_data.get('reason', '')
        is_short = self.cleaned_data.get('is_short')
        is_minor = self.cleaned_data.get('is_minor')
        ip = self.request.META['REMOTE_ADDR']

        news = super(NewsForm, self).save(commit=False)
        news.is_short = is_short
        news.last_content = content
        news.ip = ip
        if self.request.user:
            if not self.instance.pk:
                news.created_by = self.request.user
            else:
                news.updated_by = self.request.user
                news.updated_at = datetime.datetime.now()
        news.save()

        if not is_short:
            version = Version(news=news, author=self.request.user, ip=ip,
                              content=content, is_minor=is_minor,
                              reason=reason, chars_count=len(content))
            version.save()

            news.last_version = version
            news.versions_count += 1
            news.save()

        return news

    class Meta:
        model = News
        fields = ['is_short', 'title', 'content_news', 'reason', 'category',
                  'is_minor', 'status', 'closed_comments']
