from django.conf.urls import patterns, include, url
from step1.login import views, forms

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'step1.login.views.uploadFunction', name='upload'), 
	url(r'^sshcredentials/$', views.CollectSSHCredentials.as_view()),
	url(r'^connect/', views.ConnectViaSSH.as_view())
	)