from coffin.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    (r'^admin/(.*)', admin.site.root),
    (r'^account', include('pastethat.accounts.urls')),
    (r'^users', include('pastethat.profiles.urls')),
    (r'', include('pastethat.pastes.urls')),
)