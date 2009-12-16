from django.conf import settings

import time

def default(request):
    return {
        'BASE_URL': settings.BASE_URL,
        'MEDIA_URL': settings.MEDIA_URL,
        'request': request,
        'IGB': bool(request.META.get('HTTP_USER_AGENT', '').startswith('EVE-minibrowser/'))
    }