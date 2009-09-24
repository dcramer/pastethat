from coffin.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^/user\.js', views.js_user, name='accounts.jsdata'),
    url(r'^/logout$', 'django.contrib.auth.views.logout_then_login', name='accounts.logout'),
    url(r'^/login$', views.show_login, name='accounts.login'),
    url(r'^/register$', views.show_login, name='accounts.register'),
    url(r'^/settings$', views.show_settings, name='accounts.settings'),
    url(r'^/pastes$', views.show_pastes, name='accounts.pastes'),
    url(r'^/recover$', views.recover_password, name='accounts.password.recover'),
    url(r'^/recover/(?P<user_id>[\d]+)\+(?P<hash>[0-9a-zA-Z]+)$', views.recover_password_confirm, name='accounts.password.recover.confirm'),
    url(r'^/password$', views.show_change_password, name='accounts.password'),
    url(r'^$', views.show_dashboard, name='accounts'),
)