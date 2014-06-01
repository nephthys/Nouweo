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

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from vanilla import ListView, CreateView, DetailView, UpdateView, DeleteView
from .forms import IdeaForm
from .models import Idea

class IdeaCRUDView(object):
    model = Idea
    form_class = IdeaForm
    paginate_by = 2

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IdeaCRUDView, self).dispatch(*args, **kwargs)

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['request'] = self.request
        return IdeaForm(data, files, **kwargs)

    def get_success_url(self):
        redirect_to = self.request.GET.get('redirect_to', None)
        if redirect_to is not None:
            return redirect_to
        else:
            return reverse('list_ideas')

class IdeaList(IdeaCRUDView, ListView):
    template_name = 'idea_list.html'

    def get_context_data(self, **kwargs):
        context = super(IdeaList, self).get_context_data(**kwargs)
        context.update({
            'status': int(self.request.GET.get('status', 0)),
            'query': self.request.GET.get('query', '').strip(),
            'deleted': self.request.GET.get('deleted', '').strip()
        })
        return context

    def get_queryset(self):
        context = self.get_context_data()
        args = Q()
        kwargs = {}

        if context['status'] != 0:
            kwargs['status'] = context['status']

        if context['query'] != '':
            args &= (Q(title__icontains=context['query']) | \
                     Q(content__icontains=context['query']))

        if context['deleted'] != '':
            if context['deleted'] == 1:
                return Idea.deleted_objects.filter(args, **kwargs) \
                                           .select_related()
            else:
                return Idea.all_objects.filter(args, **kwargs).select_related()
        else:
            return Idea.objects.filter(args, **kwargs).select_related()

class IdeaCreate(IdeaCRUDView, CreateView):
    template_name = 'idea_form.html'

class IdeaDetail(IdeaCRUDView, DetailView):
    template_name = 'idea_detail.html'

class IdeaUpdate(IdeaCRUDView, UpdateView):
    template_name = 'idea_form.html'

class IdeaDelete(IdeaCRUDView, DeleteView):
    template_name = 'idea_confirm_delete.html'
