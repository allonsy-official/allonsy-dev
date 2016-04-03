from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^user/$', views.usr, name='user'),
    url(r'^user/(?P<username>\w+)/$', views.resolve_user_url, name='resolve_user_url'),
    url(r'^user-admin/$', views.user_admin, name='user_admin'),
    url(r'^create/$', views.create, name='create'),
    url(r'^create/account/$', views.create_account, name='create_account'),
    url(r'^create/account/do', views.do_add_account, name='do_add_account'),
    url(r'^create/organization/$', views.create_organization, name='create_organization'),
    url(r'^create/organization/do', views.do_add_organization, name='do_add_organization'),
    url(r'^create/location/$', views.create_account, name='create_account'),
    url(r'^create/location/do', views.do_add_account, name='do_add_account'),
    url(r'^create/epoch/$', views.create_account, name='create_account'),
    url(r'^create/epoch/do', views.do_add_account, name='do_add_account'),
    url(r'^assoc/org/$', views.assoc_organization, name='assoc_organization'),
    url(r'^assoc/org/do', views.do_assoc_organization, name='do_assoc_organization'),
    url(r'^assoc/org/usr/$', views.assoc_organization_user, name='assoc_organization_user'),
    url(r'^assoc/org/usr/do', views.do_assoc_organization_user, name='do_assoc_organization_user'),
    url(r'^$', views.app, name='app'),
    url(r'^login', views.do_login, name='login'),
    url(r'^logout', views.do_logout, name='logout'),
]