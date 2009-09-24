from coffin.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^/(?P<username>[a-zA-Z0-9_-]+)/pastes$', views.pastes, name='profiles.pastes'),
    url(r'^/(?P<username>[a-zA-Z0-9_-]+)$', views.details, name='profiles.details'),
)