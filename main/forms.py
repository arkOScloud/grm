from django import forms
from django.contrib import admin

from main.models import Plugin, Theme, SecretKey

class PluginForm(forms.ModelForm):
	class Meta:
		model = Plugin
		exclude = ('name', 'CATEGORIES', 'DESCRIPTION', 'LONG_DESCRIPTION', 'AUTHOR', 'APP_AUTHOR', 'MODULES', 'PLATFORMS', 'VERSION', 'DEPS', 'ICON', 'HOMEPAGE', 'APP_HOMEPAGE', 'PLUGIN_ID', 'BACKUP', 'TYPE')

class ThemeForm(forms.ModelForm):
	class Meta:
		model = Theme

class AdminPluginForm(admin.ModelAdmin):
	model = Plugin
	list_display = ('name', 'VERSION', 'data_file', 'BACKUP')

class AdminThemeForm(admin.ModelAdmin):
	model = Theme
	list_display = ('name', 'VERSION')

class SecretKeyForm(admin.ModelAdmin):
	class Meta:
		model = SecretKey
