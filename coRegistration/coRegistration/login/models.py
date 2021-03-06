from django.db import models
from django.db.models.signals import post_delete

# Create your models here.

class SSHCredentials(models.Model):
	hostname = models.CharField(max_length=200,  null=True, blank=True)
	user = models.CharField(max_length=200, unique = True, null=True, blank=True)
	password = models.CharField(max_length=200,  null=True, blank=True)
	
	def __unicode__(self):              # __unicode__ on Python 2
		return self.hostname

class Image(models.Model):
	sourceImage_rgb = models.ImageField(upload_to='in')
	sourceImage_b1 = models.ImageField(upload_to='in')
	referenceImage_b1 = models.ImageField(upload_to='in')
	epsg = models.IntegerField(blank=True, null=True) 
	
	def __unicode__(self):
		return self.image.name

def delete_imagefield(sender, **kwargs):
	tobedel = kwargs.get('instance')
	tobedel.sourceImage_rgb.delete(save=False)
	tobedel.sourceImage_b1.delete(save=False)
	tobedel.referenceImage_b1.delete(save=False)

post_delete.connect(delete_imagefield, Image)

# class LocalEnv(models.Model):
# 	localIn  = models.
# 	localOut =