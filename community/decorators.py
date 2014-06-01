from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


def permissions_required(privilege=None):
    def decorator(func):
        def inner(request, *args, **kwargs):
            permission = False
            if request.user.is_authenticated():
                if privilege:
                    permission = request.user.has_perm(privilege)
                    if not permission:
                        if '.' in privilege:
                            priv = privilege.split('.')[1]
                        else:
                            priv = privilege
                        permission = request.user.has_privilege(priv)

            if not permission:
                raise PermissionDenied

            return func(request, *args, **kwargs)
        return inner
    return decorator
