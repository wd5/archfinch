from django.views.decorators.cache import cache_page
from django.conf import settings
from staticgenerator import StaticGenerator

def expire_view_cache(request):
    from django.utils.cache import get_cache_key
    key = get_cache_key(request)
    cache.delete(key)


def cache_page_if_anonymous_user(cache_length=60):
    def decorator(func):
        def inner(*args, **kwargs):
            request = args[0]
            if request.user.is_anonymous():
                return cache_page(cache_length)(func)(*args, **kwargs)
            return func(*args, **kwargs)
        return inner

    return decorator


def publish_static(func):
    def inner(*args, **kwargs):
        request = args[0]
        response = func(*args, **kwargs)

        try:
            if ('publish' in kwargs and kwargs['publish']) or (request.user.is_anonymous() and response.publish_static):
                path = request.path
                if not path.endswith('/'):
                    path += '/'
                StaticGenerator().publish_from_path(path, '', response.content)
        except (AttributeError, KeyError) as err:
            pass

        return response
        
    return inner


def republish_static(path=''):
    import os
    from django.core.urlresolvers import resolve
    from django.http import HttpRequest, QueryDict
    from django.contrib.auth.models import AnonymousUser

    for root, dirs, files in os.walk(os.path.join(settings.WEB_ROOT, path)):
        for name in files:
            filename = os.path.join(root, name)
            relpath = '/'+os.path.relpath(filename, settings.WEB_ROOT)
            if relpath == '/index.html':
                relpath = '/'

            request = HttpRequest()
            request.path_info = relpath
            request.path = relpath
            request.user = AnonymousUser()

            #request.META.setdefault('SERVER_PORT', 80)
            #request.META.setdefault('SERVER_NAME', self.server_name)

            match = resolve(relpath)
            match.kwargs["publish"] = True
            match.args = (request,) + match.args

            match.func(*(match.args), **(match.kwargs))            
