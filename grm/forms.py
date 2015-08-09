from django import forms
from django.contrib import admin

from models import Plugin, Theme, CrashReport, Update, UpdateSignature


class PluginForm(forms.ModelForm):
    class Meta:
        model = Plugin

class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme

class AdminPluginForm(admin.ModelAdmin):
    model = Plugin
    list_display = ('name', 'VERSION', 'archive', 'BACKUP')

class AdminThemeForm(admin.ModelAdmin):
    model = Theme
    list_display = ('name', 'VERSION')

class AdminCrashForm(admin.ModelAdmin):
    model = CrashReport
    list_display = ('created_at', 'version', 'arch')

class AdminUpdateForm(admin.ModelAdmin):
    model = Update
    list_display = ('id', 'name', 'created_at')

class AdminUpdateSignatureForm(admin.ModelAdmin):
    model = UpdateSignature
    list_display = ('upd_id_list',)
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(AdminUpdateSignatureForm, self).formfield_for_foreignkey(
            db_field, request, **kwargs)
        if db_field.rel.to == Update:
            field.label_from_instance = self.get_update_id
        return field
    
    def upd_id_list(self, inst):
        return inst.update.pk

    def get_update_id(self, upd):
        return upd.id
