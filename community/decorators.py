from django.http import HttpResponse


def permissions_required(privilege=None, admin=False):
    def decorator(func):
        def inner(request, *args, **kwargs):
            permission = False
            if request.user.is_authenticated():
                if privilege:
                    permission = request.user.has_privilege(privilege)

            if permission:
                return func(request, *args, **kwargs)
            else:
                return HttpResponse('Unauthorized', status=401)
        return inner
    return decorator
