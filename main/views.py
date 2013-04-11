import os
import subprocess
import mimetypes
import sys

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

from main.models import UploadedFile
from main.forms import UploadedFileForm

def index(request):
	return (render(request, 'index.html'))

def upload(request):
	if request.method == 'POST':
		form = UploadedFileForm(request.POST, request.FILES)
		if form.is_valid():
			newfile = UploadedFile(name=request.FILES['data_file'].name, data_file=request.FILES['data_file'])
			newfile.save()
	else:
		form = UploadedFileForm()
	return render(request, 'upload.html', {'form': form})

def file(request, filename):
	upfiles = UploadedFile.objects.filter(data_file__endswith=filename)
	for upfile in upfiles:
		if os.path.basename(upfile.data_file.url) == filename:
			try:
				filepath = settings.MEDIA_ROOT + '/' + upfile.data_file.url
				download = open(filepath, 'r')
				mimetype = mimetypes.guess_type(filepath)[0]
				if not mimetype:
					mimetype = 'application/octet-stream'
				response = HttpResponse(download.read(), mimetype = mimetype)
				response['Content-Disposition'] = 'attachment; filename=%s' % filename
				return response
			except IOError:
				return render(request, 'error.html', {'error': 'Unable to open the file'})
			except:
				return render(request, 'error.html', {'error': 'Unexpected error'})
	return render(request, 'error.html', {'error': 'The file does not exist'})
