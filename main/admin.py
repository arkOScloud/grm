from django.contrib import admin

from main.models import Plugin, Theme, WebApp, SecretKey
from main.forms import AdminPluginForm, AdminThemeForm, AdminWebAppForm, SecretKeyForm

admin.site.register(Plugin, AdminPluginForm)
admin.site.register(Theme, AdminThemeForm)
admin.site.register(WebApp, AdminWebAppForm)
admin.site.register(SecretKey, SecretKeyForm)
