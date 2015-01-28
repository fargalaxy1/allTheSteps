from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^coRegistration/', include('coRegistration.login.urls')),
	)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
