import os

from django import forms
from django.db import models
from django.conf import settings

from hashlib import sha1
from random import random

def create_key():
	key = sha1(str(random())).hexdigest()
	return key[0:8]

class Plugin(models.Model):
	name			= models.CharField(max_length=255,
											 default='Plugin')
	data_file	= models.FileField(upload_to=settings.PLUGIN_ROOT)
	secret_key = models.CharField(max_length=8, default="")
	TYPE = models.CharField(max_length=255, default="")
	DESCRIPTION = models.CharField(max_length=255, default="")
	LONG_DESCRIPTION = models.CharField(max_length=999999, default="", blank=True)
	CATEGORIES = models.CharField(max_length=999, default="")
	AUTHOR = models.CharField(max_length=255, default="")
	APP_AUTHOR = models.CharField(max_length=255, default="", blank=True)
	MODULES = models.CharField(max_length=255, default=[])
	PLATFORMS = models.CharField(max_length=255, default=[])
	VERSION = models.CharField(max_length=255, default="")
	DEPS = models.CharField(max_length=255, default=[])
	ICON = models.CharField(max_length=255, default="")
	HOMEPAGE = models.CharField(max_length=255, default="")
	APP_HOMEPAGE = models.CharField(max_length=255, default="", blank=True)
	BACKUP = models.BooleanField(default=False)
	PLUGIN_ID = models.CharField(max_length=255, default="")

	def __unicode__(self):
		return os.path.basename(self.data_file.url)

class Theme(models.Model):
	name			= models.CharField(max_length=255,
											 default='Theme')
	THEME_ID = models.CharField(max_length=255, default="")
	secret_key = models.CharField(max_length=8, default="")
	theme_css = models.CharField(max_length=999999, default="")
	DESCRIPTION = models.CharField(max_length=255, default="")
	AUTHOR = models.CharField(max_length=255, default="")
	VERSION = models.CharField(max_length=255, default="")
	HOMEPAGE = models.CharField(max_length=255, default="")

class SecretKey(models.Model):
	key = models.CharField(max_length=8, default=create_key)
	admin = models.BooleanField(default=False)
