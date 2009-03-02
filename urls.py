from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'', include('pastethat.pastes.urls')),
)

handler404 = 'jinja.contrib.djangosupport.handler404'
handler500 = 'jinja.contrib.djangosupport.handler500'