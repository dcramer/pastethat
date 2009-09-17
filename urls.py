from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    (r'^admin/(.*)', admin.site.root),
    (r'', include('pastethat.pastes.urls')),
)

handler404 = 'jinja.contrib.djangosupport.handler404'
handler500 = 'jinja.contrib.djangosupport.handler500'