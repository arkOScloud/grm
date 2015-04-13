from django.contrib import admin

from models import Plugin, Theme, CrashReport, Update, UpdateSignature
from forms import AdminPluginForm, AdminThemeForm, AdminCrashForm, AdminUpdateForm, AdminUpdateSignatureForm

admin.site.register(Plugin, AdminPluginForm)
admin.site.register(Theme, AdminThemeForm)
admin.site.register(CrashReport, AdminCrashForm)
admin.site.register(Update, AdminUpdateForm)
admin.site.register(UpdateSignature, AdminUpdateSignatureForm)
