from django.conf.urls import patterns, include, url
from step1.login import views, forms

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'step1.login.views.uploadFunction', name='upload'), 
	url(r'^sshcredentials/$', views.CollectSSHCredentials.as_view()),
	url(r'^sshcredentials/connect/', views.ConnectViaSSH.as_view()),
	url(r'^runimagetoimage/', views.ConnectViaSSH.as_view()),
	url(r'^localTest/$', 'step1.login.views.testLocally', name= 'localTest')
	)