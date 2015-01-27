from django.conf.urls import patterns, include, url
from step1.login import views, forms

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.CurrentUserData.as_view()), 	
	url(r'^uploadfiles/$', 'step1.login.views.uploadFunction', name='upload'),
	# url(r'^uploadfiles/uploaddone/$', views.UploadDone.as_view()),		
	url(r'^uploadfiles/connect/$', 'step1.login.views.ConnectToRemoteHost', name= 'connect'),	
	url(r'^uploadfiles/connect/jobdone/$', views.JobDone.as_view()),	
	# url(r'^uploadfiles/connect/$', views.ConnectToRemoteHost.as_view()),
	# url(r'^sshcredentials/connect/', views.ConnectViaSSH.as_view()),
	# url(r'^runimagetoimage/', views.ConnectViaSSH.as_view()),
	# url(r'^localTest/$', 'step1.login.views.testLocally', name= 'localTest')
	)