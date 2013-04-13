from django import forms
from django.contrib import admin

from main.models import UploadedFile, SecretKey

class UploadedFileForm(forms.ModelForm):
	class Meta:
		model = UploadedFile
		exclude = ('name', 'DESCRIPTION', 'AUTHOR', 'MODULES', 'PLATFORMS', 'VERSION', 'DEPS', 'ICON', 'HOMEPAGE', 'PLUGIN_ID', 'BACKUP')

class AdminUploadedFileForm(admin.ModelAdmin):
	model = UploadedFile
	list_display = ('BACKUP', 'name', 'VERSION', 'data_file')

class SecretKeyForm(admin.ModelAdmin):
	class Meta:
		model = SecretKey
