from django.core.cache import cache

def get_or_cache(key, value, *args):
    content = cache.get(key)
    if cache.get(key) is not None:
        return content
    else:
        cache.set(key, value, *args)
        return value