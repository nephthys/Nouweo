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

from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import IntegerField, FloatField
from django.db.models.signals import post_save, post_delete


class RatingManager(object):
    def __init__(self, instance, field):
        self.content_type = None
        self.instance = instance
        self.field = field

        self.likes_field_name = '%s_likes' % (self.field.name,)
        self.dislikes_field_name = '%s_dislikes' % (self.field.name,)
        self.sum_field_name = '%s_sum' % (self.field.name,)
        self.ratio_field_name = '%s_ratio' % (self.field.name,)

    def get_content_type(self):
        if self.content_type is None:
            self.content_type = ContentType.objects.get_for_model(self.instance)
        return self.content_type

    def all(self, status=None):
        kwargs = dict(
            content_type=self.get_content_type(),
            object_id=self.instance.pk
        )

        if status is not None:
            kwargs['status'] = int(status)
        
        from models import Vote
        return Vote.objects.filter(**kwargs)

    def add(self, user, value, ip, status=None, commit=True):
        defaults = dict(
            value=value,
            ip=ip
        )

        kwargs = dict(
            content_type=self.get_content_type(),
            object_id=self.instance.pk,
            user=user
        )

        if status is not None:
            kwargs['status'] = int(status)
        
        from models import Vote
        try:
            vote, added = Vote.objects.get(**kwargs), False
        except Vote.DoesNotExist:
            kwargs.update(defaults)
            vote, added = Vote.objects.create(**kwargs), True

        if added:
            self.update_count()

        return {'added': added, 'value': vote.value}

    def update_count(self, commit=True):
        kwargs = {}
        count_field = self.field.count_status

        if count_field is not None:
            if count_field == 'status' and hasattr(self.instance, 'status'):
                kwargs['status'] = int(self.instance.status)
            else:
                kwargs['status'] = self.field.count_status

        all_votes = self.all(**kwargs)
        likes = [r.value for r in all_votes if r.value > 0]
        dislikes = [r.value for r in all_votes if r.value < 0]
        votes = likes + dislikes

        count_val = len(votes)
        likes_val = len(likes)
        dislikes_val = len(dislikes)
        sum_val = sum(votes)
        ratio_val = 0 if count_val == 0 else likes_val * 100 / count_val

        setattr(self.instance, self.likes_field_name, likes_val)
        setattr(self.instance, self.dislikes_field_name, dislikes_val)
        setattr(self.instance, self.sum_field_name, sum_val)
        setattr(self.instance, self.ratio_field_name, ratio_val)

        output = {self.likes_field_name: likes_val,
                  self.dislikes_field_name: dislikes_val,
                  self.sum_field_name: sum_val,
                  self.ratio_field_name: ratio_val}

        if commit:
            self.instance.save()

        return output

    def has_voted(self, user, status=None):
        kwargs = dict(
            content_type=self.get_content_type(),
            object_id=self.instance.pk,
            user=user
        )

        if status is not None:
            kwargs['status'] = int(status)

        from models import Vote
        count = Vote.objects.filter(**kwargs).count()

        return (count > 0)


class RatingCreator(object):
    def __init__(self, field):
        self.field = field
        self.likes_field_name = '%s_likes' % (self.field.name,)
        self.dislikes_field_name = '%s_dislikes' % (self.field.name,)
        self.sum_field_name = '%s_sum' % (self.field.name,)
        self.ratio_field_name = '%s_ratio' % (self.field.name,)

    def __get__(self, instance, type=None):
        if instance is None:
            return self.field
        return RatingManager(instance, self.field)


class RatingField(IntegerField):
    def __init__(self, *args, **kwargs):
        self.can_change_vote = kwargs.pop('can_change_vote', False)
        self.allow_delete = kwargs.pop('allow_delete', False)
        self.count_status = kwargs.pop('count_status', None)

        kwargs['editable'] = False
        kwargs['default'] = 0
        kwargs['blank'] = True

        super(RatingField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        self.name = name

        fields_kwargs = dict(editable=False, default=0, blank=True)

        self.likes_field = IntegerField(**fields_kwargs)
        cls.add_to_class('%s_likes' % (self.name,), self.likes_field)

        self.dislikes_field = IntegerField(**fields_kwargs)
        cls.add_to_class('%s_dislikes' % (self.name,), self.dislikes_field)

        self.sum_field = IntegerField(**fields_kwargs)
        cls.add_to_class('%s_sum' % (self.name,), self.sum_field)

        self.ratio_field = FloatField(**fields_kwargs)
        cls.add_to_class('%s_ratio' % (self.name,), self.ratio_field)

        field = RatingCreator(self)
        setattr(cls, name, field)


class CommentsField(GenericRelation):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('object_id_field', 'object_pk')
        kwargs.setdefault('to', 'community.ThreadedComment')

        super(CommentsField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        self.name = name

        super(CommentsField, self).contribute_to_class(cls, name)

        self.count_field = IntegerField(editable=False, default=0)
        cls.add_to_class('%s_count' % (self.name,), self.count_field)

        getter_name = "get_%s_name" % self.__class__.__name__.lower()
        cls.add_to_class(getter_name, lambda self: name)

        post_save.connect(self.related_items_changed)
        post_delete.connect(self.related_items_changed)

    def related_items_changed(self, **kwargs):
        try:
            to = self.rel.to
            if isinstance(to, basestring):
                to = get_model(*to.split('.', 1))
            if not isinstance(kwargs['instance'], to):
                raise TypeError
        except (TypeError, ValueError):
            return
        for_model = kwargs['instance'].content_type.model_class()
        if issubclass(for_model, self.model):
            instance_id = kwargs['instance'].object_pk
            try:
                instance = for_model.objects.get(id=instance_id)
            except self.model.DoesNotExist:
                return
            if hasattr(instance, 'get_content_model'):
                instance = instance.get_content_model()
            related_manager = getattr(instance, self.name)
            try:
                count = related_manager.count_queryset()
            except AttributeError:
                count = related_manager.count()

            count_field_name = '%s_count' % self.name
            setattr(instance, count_field_name, count)
            instance.save()
