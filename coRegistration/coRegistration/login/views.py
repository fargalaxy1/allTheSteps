from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from django.views.generic import FormView, TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.context import RequestContext
from django.conf import settings
from django.http import HttpResponse

from coRegistration.login import forms
from coRegistration.login.models import Image
from coRegistration.login.forms import ImageForm
from .utils import remoteHost_Setup_and_upload, remote_run_routine_and_save, copyRunCode_and_set_conf_files_inRemoteHost, cleanUp

from django.db.models.signals import post_delete
import logging
import getpass
import shutil
import socket
import os
import time
logger = logging.getLogger("coRegistration." + __name__)

currentUserName = 0
currentUserEmail = 0

ssh_hostname = '139.191.9.230'
ssh_username = 'giovamt'
ssh_password = 'jrc2015'

webDomain = 'http://127.0.0.1:8000'
class CurrentUserData(FormView):
	logger.debug("class CurrentUserData")
	
	template_name="currentUserData.html"
	form_class=forms.CurrentUserForm
	success_url = 'uploadfiles/'

	def form_valid(self, form):
		global currentUserName, currentUserEmail
		currentUserName = form.cleaned_data['currentUserName']
		currentUserEmail = form.cleaned_data['currentUserEmail']
		print 'form_valid' 
		return super(CurrentUserData, self).form_valid(form)

def purgeOldOutput(currentUserName = None):
	tobeRemoved = settings.MEDIA_ROOT+ '/out/' + currentUserName + '_output.tif'
	try:
		os.remove(tobeRemoved)
	except OSError:
		print("file not removed %s" % tobeRemoved)		
		pass

def uploadFunction(request):
	logger.debug("class uploadFunction")
	global currentUserName

	purgeOldOutput(currentUserName)

	imagesCounter = Image.objects.filter(pk=1).count()
	if imagesCounter:
		images = Image.objects.all()
		if request.method == 'POST':
			if 'confirm_inputimgs' in request.POST:
				logger.debug("confirm uploaded files")
				return HttpResponseRedirect('uploaddone/')

			elif 'update_inputimgs' in request.POST:
				logger.debug("update files")
				tobedeleted = Image.objects.filter(pk=1)
				tobedeleted.delete()
				return HttpResponseRedirect(reverse("upload"))
		else:
			return render_to_response(
			'uploadedFiles.html',
			{'images': images},
			context_instance=RequestContext(request)
			)

	else :
    # Handle file upload
		if request.method == 'POST':
			logger.debug("POST form")
			form = ImageForm(request.POST, request.FILES)
			logger.debug(request.FILES.keys()) 
			logger.debug(request.POST.keys()) 

			if form.is_valid():
				newsrc_b1 = Image(sourceImage_b1 = request.FILES['sourceImage_b1'],
					sourceImage_rgb = request.FILES['sourceImage_rgb'],
					referenceImage_b1 = request.FILES['referenceImage_b1'],
					epsg = request.POST['epsg']
					)

				newsrc_b1.save()
				logger.debug("POST form 2")

				# Redirect to the document list after POST
				return HttpResponseRedirect('uploaddone/')

		else:
			logger.debug("else form")
			form = ImageForm() # A empty, unbound form

		# Load documents for the list page
		images = Image.objects.all()

		# Render list page with the documents and the form
		return render_to_response(
			'uploadFiles.html',
			{'images': images, 'form': form},
		context_instance=RequestContext(request)
		)

class CollectSSHCredentials(FormView):
	logger.debug("class CollectSSHCredentials")
	
	template_name="collectSSHCredentials.html"
	form_class=forms.SshCredentialsForm
	success_url = 'connect/'
	print getpass.getuser()
   
	def form_valid(self, form):
		hostname = form.cleaned_data['hostname']
		user = form.cleaned_data['user']
		password = form.cleaned_data['password']
		form.save(commit = True)
		return super(CollectSSHCredentials, self).form_valid(form)

def sendEmailWithOutput():
	e_object = 'Your image co-registation job is done'
	e_body = 'Dowload your files ' + webDomain + '/media/out/' + currentUserName + '_output.tif'
	send_mail(e_object, e_body, 'martina.giovalli@jrc.ec.europa.eu',
    [currentUserEmail], fail_silently=False)

def ConnectToRemoteHost(request):
 	logger.debug("function ConnectToRemoteHost")

	global ssh_hostname, ssh_username, ssh_password, currentUserName 
	remoteHost_Setup_and_upload(currentUserName, ssh_hostname, ssh_username, ssh_password)
	copyRunCode_and_set_conf_files_inRemoteHost(currentUserName, ssh_hostname, ssh_username, ssh_password)
	
	remote_run_routine_and_save(currentUserName, ssh_hostname, ssh_username, ssh_password)
	
	sendEmailWithOutput()

	# below, code for deleting the remote currentuser working folder
	# not working properly, no time to fix

	# outputFilePath = settings.MEDIA_ROOT + '/out/' + currentUserName+ '_output.tif'		
	# while not os.path.exists(outputFilePath):
	# 	print("os.path.exists(outputFilePath) %s" % (os.path.exists(outputFilePath)))
	# 	print("while not os.path.exists %s " % outputFilePath)
	# 	time.sleep(1)
	# if os.path.isfile(outputFilePath):
	# 	cleanUp(currentUserName, ssh_hostname, ssh_username, ssh_password)
	# 	sendEmailWithOutput()
	# else:
	# 	raise ValueError("%s isn't a file!" % outputFilePath)
	
	return HttpResponseRedirect('jobdone/')

def uploadDone(request):
	logger.debug("function uploadDone")
	return render_to_response('launchJob.html')

def jobDone(request):
	logger.debug("function jobDone")
	linkToOutputFile = webDomain + '/media/out/' + currentUserName + '_output.tif'
	return render_to_response('jobDone.html', {'linkToOutputFile': linkToOutputFile})
