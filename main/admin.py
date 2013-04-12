from django.contrib import admin

from main.models import UploadedFile
from main.forms import AdminUploadedFileForm

admin.site.register(UploadedFile, AdminUploadedFileForm)
