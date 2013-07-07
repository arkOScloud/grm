from django.contrib import admin

from main.models import Plugin, Theme, SecretKey
from main.forms import AdminPluginForm, AdminThemeForm, SecretKeyForm

admin.site.register(Plugin, AdminPluginForm)
admin.site.register(Theme, AdminThemeForm)
admin.site.register(SecretKey, SecretKeyForm)
