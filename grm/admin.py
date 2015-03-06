from django.contrib import admin

from models import Plugin, Theme, CrashReport
from forms import AdminPluginForm, AdminThemeForm, AdminCrashForm

admin.site.register(Plugin, AdminPluginForm)
admin.site.register(Theme, AdminThemeForm)
admin.site.register(CrashReport, AdminCrashForm)
