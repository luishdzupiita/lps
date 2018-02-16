# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.landing_page, name='landing_page'),
    url(r'^lps/$', views.lps, name='lps'),
    url(r'^cs/$', views.cs, name='cs'),
]
