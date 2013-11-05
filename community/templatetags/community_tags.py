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

from django import template
from community.models import Vote

register = template.Library()


class VotedForObjectsNode(template.Node):
    def __init__(self, objects):
        self.objects = objects

    def render(self, context):
        try:
            objects = template.resolve_variable(self.objects, context)
        except template.VariableDoesNotExist:
            return ''

        user = context.get('user')
        votes_list = Vote.objects.has_voted_in_bulk(objects, user)

        for obj in objects:
            has_voted = False
            vote = votes_list.get(obj.id, None)

            if vote is not None and 'value' in vote:
                has_voted = True
                obj.user_vote = vote['value']

            obj.has_voted = has_voted

        context[self.objects] = objects
        return ''
        
@register.tag('voted_for_objects')  
def has_voted_for_objects(parser, token):
    """
    Retrieves the total scores for a list of objects and the number of
    votes they have received and stores them in a context variable.

    Example usage::

        {% voted_for_objects posts_list %}
    """
    bits = token.contents.split()
    return VotedForObjectsNode(bits[1])


@register.inclusion_tag('includes/rating.html', takes_context=True)
def rating_for(context, obj, *args, **kwargs):
    model = kwargs.get('model', None)
    context['rating_obj'] = obj
    context['rating_model'] = model
    return context
