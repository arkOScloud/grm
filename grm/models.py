import os

from django import forms
from django.db import models
from django.conf import settings

from hashlib import sha1
from random import random

class Plugin(models.Model):
    name = models.CharField(max_length=255, default='Plugin')
    archive = models.FileField()
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
        return os.path.basename(self.archive.url)

class Theme(models.Model):
    name = models.CharField(max_length=255, default='Theme')
    THEME_ID = models.CharField(max_length=255, default="")
    theme_css = models.CharField(max_length=999999, default="")
    DESCRIPTION = models.CharField(max_length=255, default="")
    AUTHOR = models.CharField(max_length=255, default="")
    VERSION = models.CharField(max_length=255, default="")
    HOMEPAGE = models.CharField(max_length=255, default="")

class Image(models.Model):
    itype = models.CharField(default="", max_length=255)
    plugin = models.ForeignKey(Plugin, related_name='images')
    image = models.FileField()

class CrashReport(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    trace = models.TextField(max_length=99999, default="")
    summary = models.TextField(max_length=99999, default="")
    report = models.TextField(max_length=99999, default="")
    version = models.TextField(max_length=255, default="")
    arch = models.TextField(max_length=255, default="")

class Update(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    info = models.TextField(max_length=99999, default="")
    name = models.TextField(max_length=255, default="")
    tasks = models.TextField(max_length=99999, default="")

class UpdateSignature(models.Model):
    update = models.OneToOneField(Update, related_name='signature')
    sig = models.TextField(max_length=99999, default="")
