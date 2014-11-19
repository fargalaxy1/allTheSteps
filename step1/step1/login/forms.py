from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import SSHCredentials
import logging


logger = logging.getLogger("step1." + __name__)

class ImageForm(forms.Form):
    logger.debug("class ImageForm")

    sourceImage = forms.ImageField(
        label='Select source image')
    referenceImage = forms.ImageField(
        label='Select reference image')


class SshCredentialsForm(forms.ModelForm):
    """
    credential fields
    """
    logger.debug("class SshCredentialsForm")
    class Meta:
        model = SSHCredentials
        # logger.debug("END class SshCredentialsForm")

