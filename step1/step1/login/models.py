from django.db import models

# Create your models here.

class SSHCredentials(models.Model):
	hostname = models.CharField(max_length=200,  null=True, blank=True)
	user = models.CharField(max_length=200,  null=True, blank=True)
	password = models.CharField(max_length=200,  null=True, blank=True)

class Image(models.Model):
	sourceImage = models.ImageField(upload_to='test')
	referenceImage = models.ImageField(upload_to='test')	 
	def __unicode__(self):
		return self.image.name
