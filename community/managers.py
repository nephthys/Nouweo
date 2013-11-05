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

from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager


class VoteManager(Manager):
    def has_voted_in_bulk(self, objects, user, status=None):
        object_ids = [o._get_pk_val() for o in objects]
        if not object_ids:
            return {}

        first_object = objects[0]

        # Object has parent?
        if len(first_object._meta.parents.keys()) > 0:
            first_object = first_object._meta.parents.keys()[-1]

        ctype = ContentType.objects.get_for_model(first_object)

        kwargs = dict(
            object_id__in=object_ids,
            content_type=ctype,
            user=user
        )

        if status is not None:
            kwargs['status'] = int(status)

        queryset = self.filter(**kwargs).values('object_id', 'value',
                                                'user_id')

        vote_dict = {}
        for row in queryset:
            vote_dict[row['object_id']] = {
                'value': int(row['value']),
                'user_id': int(row['user_id']),
            }

        return vote_dict
