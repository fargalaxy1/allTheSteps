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

from step1.login import forms
from step1.login.models import Image
from step1.login.forms import ImageForm
from .utils import remoteHost_Setup_and_upload, remote_run_routine_and_save, copyRunCode_and_set_conf_files_inRemoteHost

from django.db.models.signals import post_delete
import logging
import getpass
import shutil
import socket
logger = logging.getLogger("step1." + __name__)

currentUserName = 0
currentUserEmail = 0

ssh_hostname = '139.191.9.230'
ssh_username = 'giovamt'
ssh_password = 'jrc2015'

class CurrentUserData(FormView):
	logger.debug("class CurrentUserData")
	
	template_name="currentUserData.html"
	form_class=forms.CurrentUserForm
	# success_url = 'uploadfiles/'
	success_url = 'uploadfiles/'

	# print getpass.getuser()
   
	def form_valid(self, form):
		global currentUserName, currentUserEmail
		currentUserName = form.cleaned_data['currentUserName']
		currentUserEmail = form.cleaned_data['currentUserEmail']
		print 'form_valid' 
		return super(CurrentUserData, self).form_valid(form)

def uploadFunction(request):
	logger.debug("class uploadFunction")
	global currentUserName
	print('uploadFunction %s' % currentUserName)
	print('uploadFunction %s' % currentUserEmail)

	imagesCounter = Image.objects.filter(pk=1).count()
	if imagesCounter:
		images = Image.objects.all()
		if request.method == 'POST':
			if 'confirm_inputimgs' in request.POST:
				logger.debug("confirm uploaded files")
				return HttpResponseRedirect('connect/')
				#return HttpResponseRedirect('localTest/')
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
				# newsrc_rgb = Image(sourceImage_rgb = request.FILES['sourceImage_rgb'])
				# newsrc_rgb.save()
				# newref_b1 = Image(referenceImage_b1 = request.FILES['referenceImage_b1'])
				# newref_b1.save()
				logger.debug("POST form 2")

				# Redirect to the document list after POST
				return HttpResponseRedirect('connect/')
				#return HttpResponseRedirect('localTest/')

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
	e_body = 'Dowload your files ' + 'http://127.0.0.1:8000/media/out/' + currentUserName + '_output.tif'
	send_mail(e_object, e_body, 'martina.giovalli@jrc.ec.europa.eu',
    [currentUserEmail], fail_silently=False)


def ConnectToRemoteHost(request):
 	logger.debug("function ConnectToRemoteHost")

	global ssh_hostname, ssh_username, ssh_password, currentUserName 
	remoteHost_Setup_and_upload(currentUserName, ssh_hostname, ssh_username, ssh_password)
	copyRunCode_and_set_conf_files_inRemoteHost(currentUserName, ssh_hostname, ssh_username, ssh_password)
	remote_run_routine_and_save(currentUserName, ssh_hostname, ssh_username, ssh_password)
	sendEmailWithOutput()

	return HttpResponseRedirect('jobdone/')

class UploadDone(TemplateView):
	template_name="connectSSH.html"	
	# def get(self, request, *args, **kwargs):
	# 	template_name="connectSSH.html"	
	# 	return HttpResponseRedirect('connect/')

class JobDone(TemplateView):
	logger.debug("class JobDone")
	template_name="jobDone.html"

def downloadFunction(request, user_name):
	logger.debug("function downloadFunction")
	filename = settings.MEDIA_URL+ 'out/' + user_name + '_output.tif'
	print filename
	response = HttpResponse(filename, content_type='image/tiff')
	response['Content-Disposition'] = 'attachment; filename=' + filename
	return response

	# context = {"user_name": user_name}
	# return render_to_response("download_output.html",
	# 	context_instance=RequestContext(request, context)
	# 	)