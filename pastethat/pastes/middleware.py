from django.conf import settings
from django.http import HttpResponseRedirect

from models import Group

class GroupProcessorMiddleware(object):
    def process_request(self, request):
        if request.META['HTTP_HOST'] == settings.BASE_DOMAIN:
            # Handles the non-www case
            return HttpResponseRedirect('http://www.%s%s' % (settings.BASE_DOMAIN, request.get_full_path()))
        settings.GROUP_DOMAIN = request.META['HTTP_HOST'].replace('.' + settings.BASE_DOMAIN, '')
        if settings.BASE_DOMAIN:
            settings.BASE_URL = 'http://%s.%s' % (settings.GROUP_DOMAIN, settings.BASE_DOMAIN)
        else: # this makes local work
            settings.BASE_URL = 'http://%s' % (settings.GROUP_DOMAIN,)
        request.group, created = Group.objects.get_or_create(
            subdomain   = settings.GROUP_DOMAIN,
            defaults    = dict(
                name=settings.GROUP_DOMAIN,
            ),
        )
