from django import forms
from django.contrib import admin

from models import Plugin, Theme, CrashReport

class PluginForm(forms.ModelForm):
	class Meta:
		model = Plugin

class ThemeForm(forms.ModelForm):
	class Meta:
		model = Theme

class AdminPluginForm(admin.ModelAdmin):
	model = Plugin
	list_display = ('name', 'VERSION', 'data_file', 'BACKUP')

class AdminThemeForm(admin.ModelAdmin):
	model = Theme
	list_display = ('name', 'VERSION')

class AdminCrashForm(admin.ModelAdmin):
	model = CrashReport
	list_display = ('created_at',)
