from django.conf.urls import patterns, include, url
from coRegistration.login import views, forms

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.CurrentUserData.as_view()), 	
	url(r'^uploadfiles/$', 'coRegistration.login.views.uploadFunction', name='upload'),
	url(r'^uploadfiles/uploaddone/$', 'coRegistration.login.views.uploadDone', name='uploaddone'),		
	url(r'^uploadfiles/uploaddone/connect/$', 'coRegistration.login.views.ConnectToRemoteHost', name= 'connect'),	
	url(r'^uploadfiles/uploaddone/connect/jobdone/$', 'coRegistration.login.views.jobDone'),	
	)