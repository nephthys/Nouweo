from django.contrib.auth import get_user_model
from django.utils.timezone import now
from posts.models import Category
from .models import KarmaPrivilege
from .utils import get_or_cache

class UserSettingsMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            user = get_user_model()
            user.objects.filter(pk=request.user.pk).update(last_visit=now())

            permissions_karma = {}

            categories = get_or_cache('global_categories', \
                Category.objects.all(), 60*60)

            permissions = get_or_cache('global_karma_privileges', \
                KarmaPrivilege.objects.all().select_related('permission', \
                    'permission__content_type'), 60*60)

            for perm in permissions:
                key = '%s.%s' % (perm.permission.content_type.app_label, \
                                 perm.permission.codename)

                permissions_karma[key] = perm.minimum_points

            request.permissions_karma = permissions_karma
            request.categories = categories