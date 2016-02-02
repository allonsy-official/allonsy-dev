from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^user/', views.usr, name='user'),
    url(r'^$', views.app, name='app'),
    url(r'^login', views.do_login, name='login'),
    url(r'^logout', views.do_logout, name='login'),
]