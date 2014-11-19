from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import FormView, TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from step1.login import forms
from step1.login.models import Image
from step1.login.forms import ImageForm
from .utils import connect_via_SSH_and_upload
import logging
import getpass

logger = logging.getLogger("step1." + __name__)

def uploadFunction(request):
	logger.debug("class uploadFunction")

    # Handle file upload
	if request.method == 'POST':
		logger.debug("POST form")
		form = ImageForm(request.POST, request.FILES)
		if form.is_valid():
			newsrc = Image(sourceImage = request.FILES['sourceImage'])
			newsrc.save()
			print newsrc
			newref = Image(referenceImage = request.FILES['referenceImage'])
			newref.save()
			print newref

			# Redirect to the document list after POST
			return HttpResponseRedirect('sshcredentials/')
	else:
		logger.debug("else form")
		form = ImageForm() # A empty, unbound form

	# Load documents for the list page
	images = Image.objects.filter()
	
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
