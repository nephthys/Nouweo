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

            if permission:
                return func(request, *args, **kwargs)
            else:
                return HttpResponse('Unauthorized', status=401)
        return inner
    return decorator
