from django.contrib import admin

from main.models import UploadedFile, SecretKey
from main.forms import AdminUploadedFileForm, SecretKeyForm

admin.site.register(UploadedFile, AdminUploadedFileForm)
admin.site.register(SecretKey, SecretKeyForm)
