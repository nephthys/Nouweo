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

from django.contrib.auth import get_user_model
from django.contrib import admin
from models import *


class KarmaPrivilegeAdmin(admin.ModelAdmin):
	list_display = ('name', 'identifier', 'minimum_points', 'users_concerned')

	def users_concerned(self, obj):
		return get_user_model().objects.filter(karma__gt=obj.minimum_points).count()

admin.site.register(User)
admin.site.register(KarmaAction)
admin.site.register(KarmaChange)
admin.site.register(KarmaPrivilege, KarmaPrivilegeAdmin)
