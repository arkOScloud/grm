from django import forms

from main.models import UploadedFile

class UploadedFileForm(forms.ModelForm):
	class Meta:
		model = UploadedFile
		exclude = ('name',)
