import os

from django.db import models
from django.conf import settings

class UploadedFile(models.Model):
	name			= models.CharField(max_length=255,
											 default='Plugin')
	data_file	= models.FileField(upload_to=settings.UPLOADEDFILE_ROOT)
	DESCRIPTION = models.CharField(max_length=255, default="")
	AUTHOR = models.CharField(max_length=255, default="")
	MODULES = models.CharField(max_length=255, default=[])
	PLATFORMS = models.CharField(max_length=255, default=[])
	VERSION = models.CharField(max_length=255, default="")
	DEPS = models.CharField(max_length=255, default=[])
	ICON = models.ImageField(upload_to=settings.ICON_FOLDER)
	HOMEPAGE = models.CharField(max_length=255, default="")
	PLUGIN_ID = models.CharField(max_length=255, default="")

	def __unicode__(self):
		return os.path.basename(self.data_file.url)
