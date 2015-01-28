from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import SSHCredentials
import logging


logger = logging.getLogger("coRegistration." + __name__)

class ImageForm(forms.Form):
    logger.debug("class ImageForm")

    sourceImage_b1 = forms.ImageField(
        label='Select monochromatic source image ')
    sourceImage_rgb = forms.ImageField(
        label='Select rgb source image')
    referenceImage_b1 = forms.ImageField(
        label='Select monochromatic reference image')
    epsg = forms.IntegerField(
        label='Input EPSG number')


class SshCredentialsForm(forms.ModelForm):
    """
    credential fields
    """
    logger.debug("class SshCredentialsForm")
    class Meta:
        model = SSHCredentials
        widgets = {
        'password': forms.PasswordInput(),
        }
        # logger.debug("END class SshCredentialsForm")

class CurrentUserForm(forms.Form):
    logger.debug("class CurrentUserForm")

    currentUserName = forms.CharField(label='Type in your username ')
    currentUserEmail = forms.EmailField(label='Type in your email ')