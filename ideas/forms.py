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

from django.forms import ModelForm
from django.utils.translation import ugettext as _
from .models import Idea
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import FormActions
import datetime

class IdeaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        if not kwargs.pop('small_display', False):
            self.helper.form_class = 'form-horizontal'
            self.helper.label_class = 'col-sm-2 control-label'
            self.helper.field_class = 'col-sm-10'
        self.helper.layout = Layout(
            Field('title', css_class='input-xlarge'),
            Field('content', rows='3', css_class='input-xlarge'),
            FormActions(
                Submit('send', _('Send'), css_class='btn-primary')
            )
        )
        self.request = kwargs.pop('request', None)
        super(IdeaForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        idea = super(IdeaForm, self).save(commit=False)
        if not self.instance.pk:
            if self.request.user:
                idea.created_by = self.request.user
            if self.request.META['REMOTE_ADDR']:
                idea.ip = self.request.META['REMOTE_ADDR']
        else:
            if self.request.user:
                idea.updated_by = self.request.user

            idea.updated_at = datetime.datetime.now()
        idea.save()
        return idea

    class Meta:
        model = Idea
        fields = ['title', 'content']