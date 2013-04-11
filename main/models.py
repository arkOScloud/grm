import os

from django.db import models
from django.conf import settings

#class UploadedFileManager(models.Manager):
#	def getAllAccordingFilename(self, filename):
#		result = UploadedFile.objects.filter(data_file.url__endswith=filename)

class UploadedFile(models.Model):
	name			= models.CharField(max_length=255,
											 default='UploadedFile object')
	data_file	= models.FileField(upload_to=settings.UPLOADEDFILE_ROOT)

	def __unicode__(self):
		return os.path.basename(self.data_file.url)
