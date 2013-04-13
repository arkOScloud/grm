import os

from django.db import models
from django.conf import settings

from hashlib import sha1
from random import random

def create_key():
	key = sha1(str(random())).hexdigest()
	return key[0:8]

class UploadedFile(models.Model):
	name			= models.CharField(max_length=255,
											 default='Plugin')
	data_file	= models.FileField(upload_to=settings.UPLOADEDFILE_ROOT)
	secret_key = models.CharField(max_length=8, default="")
	DESCRIPTION = models.CharField(max_length=255, default="")
	AUTHOR = models.CharField(max_length=255, default="")
	MODULES = models.CharField(max_length=255, default=[])
	PLATFORMS = models.CharField(max_length=255, default=[])
	VERSION = models.CharField(max_length=255, default="")
	DEPS = models.CharField(max_length=255, default=[])
	ICON = models.ImageField(upload_to=settings.ICON_FOLDER)
	HOMEPAGE = models.CharField(max_length=255, default="")
	BACKUP = models.BooleanField(default=False)
	PLUGIN_ID = models.CharField(max_length=255, default="")

	def __unicode__(self):
		return os.path.basename(self.data_file.url)

class SecretKey(models.Model):
	key = models.CharField(max_length=8, default=create_key)
