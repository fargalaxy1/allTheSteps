from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import FormView, TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from step1.login import forms
from step1.login.models import Image
from step1.login.forms import ImageForm
from .utils import connect_via_SSH_and_upload, setup_configuration_files, run_routine_and_save
from .utils import test_setup_and_upload

from django.db.models.signals import post_delete
import logging
import getpass
import shutil
logger = logging.getLogger("step1." + __name__)


def uploadFunction(request):
	logger.debug("class uploadFunction")
	imagesCounter = Image.objects.filter(pk=1).count()
	if imagesCounter:
		images = Image.objects.all()
		if request.method == 'POST':
			if 'confirm_inputimgs' in request.POST:
				logger.debug("confirm uploaded files")
				# return HttpResponseRedirect('sshcredentials/')
				return HttpResponseRedirect('localTest/')
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

				# Redirect to the document list after POST
				# return HttpResponseRedirect('sshcredentials/')
				return HttpResponseRedirect('localTest/')

		else:
			logger.debug("else form")
			form = ImageForm() # A empty, unbound form

		# Load documents for the list page
		images = Image.objects.all()
		logger.debug("init images model")


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
		connect_via_SSH_and_upload(hostname, user, password)
		return super(CollectSSHCredentials, self).form_valid(form)

class ConnectViaSSH(TemplateView):
	logger.debug("class ConnectViaSSH")
	template_name="connectSSH.html"

def testLocally(request):
	userName = 'giovamt'
	roothPath = '/home/giovamt/webAppFolder/imageToImage/'
	currentUsrLocalInPath = test_setup_and_upload(roothPath, userName);
	currentUsrLocalHomePath = roothPath + 'users/' + userName + '/'
	setup_configuration_files(currentUsrLocalInPath, currentUsrLocalHomePath);
	run_routine_and_save(currentUsrLocalHomePath);

	return HttpResponseRedirect('sshcredentials/')
