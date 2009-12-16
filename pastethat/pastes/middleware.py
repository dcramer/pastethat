from django.conf import settings

from models import Group

class GroupProcessorMiddleware(object):
    def process_request(self, request):
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
