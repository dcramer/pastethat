from coffin.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.new_paste, name='pastes.new'),
    url(r'^recent$', views.recent_pastes, name='pastes.recent'),
    url(r'^([A-Za-z0-9_-]+)(?:/syntax/([a-zA-Z0-9_-]+))?$', views.view_paste, name='pastes.details'),
    url(r'^([A-Za-z0-9_-]+)/followup$', views.post_followup, name='pastes.followup'),
    url(r'^([A-Za-z0-9_-]+)/children$', views.view_children, name='pastes.children'),
    url(r'^([A-Za-z0-9_-]+)/edit$', views.edit_paste, name='pastes.edit'),
    url(r'^([A-Za-z0-9_-]+)/get$', views.download_paste, name='pastes.download'),
    url(r'^([A-Za-z0-9_-]+)\.jpg$', views.view_thumbnail, name='pastes.thumbnail'),
)
