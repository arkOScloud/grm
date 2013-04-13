import os
import subprocess
import mimetypes
import sys

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.core.files import File

from main.models import UploadedFile, SecretKey
from main.forms import UploadedFileForm

def reload_list():
	pluginlist = []
	plugins = UploadedFile.objects.filter(BACKUP=False)
	for data in plugins:
		entry = {'description': data.DESCRIPTION, 'author': data.AUTHOR, 'modules': data.MODULES, 'platforms': data.PLATFORMS, 'version': data.VERSION, 'deps': data.DEPS, 'icon': settings.HOSTNAME + '/icon/' + data.PLUGIN_ID, 'homepage': data.HOMEPAGE, 'id': data.PLUGIN_ID, 'name': data.name}
		pluginlist.append(entry)
	return pluginlist

def index(request):
	return (render(request, 'index.html'))

def upload(request):
	if request.method == 'POST':
		form = UploadedFileForm(request.POST, request.FILES)
		keys = SecretKey.objects.all()

		# Check validity of provided secret key
		try:
			SecretKey.objects.get(key=request.POST['secret_key'])
		except:
			return render(request, 'error.html', {'error': 'Secret key incorrect'})

		# Only upload the file if it is a gzipped archive
		if request.FILES['data_file'].content_type == 'application/gzip':
			newfile = UploadedFile(name=request.FILES['data_file'].name, data_file=request.FILES['data_file'], secret_key=request.POST['secret_key'])
			newfile.save()

			file = UploadedFile.objects.get(name=request.FILES['data_file'].name)
			temp = settings.MEDIA_ROOT + settings.TEMP_FOLDER

			# Untar the archive to a temp location and read its data
			untar = subprocess.Popen(['tar', 'xvzf', file.data_file.path, '-C', temp], stdout=subprocess.PIPE)
			comm = untar.communicate()[0]
			comm = comm.split('\n')[0]
			directory = comm[:-len("/")]
			try:
				data = read_config(temp + directory)
			except:
				newfile.delete()
				subprocess.call(['rm', '-r', temp + directory])
				return render(request, 'error.html', {'error': 'Malformed archive. Please resubmit in accordance with Genesis Plugin API guidelines.'})
			finally:
				subprocess.call(['rm', '-r', temp + directory])

			# Create a backup if a matching plugin already exists
			if UploadedFile.objects.filter(PLUGIN_ID=directory).exists():
				backup(UploadedFile.objects.get(PLUGIN_ID=directory))

			# Update the database with the new plugin data
			file.name = data.NAME
			file.DESCRIPTION = data.DESCRIPTION
			file.AUTHOR = data.AUTHOR
			file.MODULES = data.MODULES
			file.PLATFORMS = data.PLATFORMS
			file.VERSION = data.VERSION
			file.DEPS = data.DEPS
			file.HOMEPAGE = data.HOMEPAGE
			file.PLUGIN_ID = directory
			file.ICON.save(directory + '.png', File(open(temp + directory + '/files/icon.png')))
			file.BACKUP = False

		else:
			return render(request, 'error.html', {'error': 'Form not valid, or file not of acceptable type'})
	else:
		form = UploadedFileForm()
	return render(request, 'upload.html', {'form': form})

def file(request, id):
	# Serve up the plugin archive file
	getfiles = UploadedFile.objects.all()
	for getfile in getfiles:
		if os.path.basename(getfile.PLUGIN_ID) == id:
			try:
				filepath = settings.MEDIA_ROOT + '/' + getfile.data_file.url
				download = open(filepath, 'r')
				mimetype = mimetypes.guess_type(filepath)[0]
				if not mimetype:
					mimetype = 'application/octet-stream'
				response = HttpResponse(download.read(), mimetype = mimetype)
				response['Content-Disposition'] = 'attachment; filename="plugin.tar.gz"'
				return response
			except IOError:
				return render(request, 'error.html', {'error': 'Unable to open the file'})
			except:
				return render(request, 'error.html', {'error': 'Unexpected error'})
	return render(request, 'error.html', {'error': 'The file does not exist'})

def icon(request, id):
	# Serve up the plugin icon
	geticons = UploadedFile.objects.all()
	for geticon in geticons:
		if os.path.basename(geticon.PLUGIN_ID) == id:
			try:
				filepath = settings.MEDIA_ROOT + '/' + geticon.ICON.url
				download = open(filepath, 'r')
				mimetype = mimetypes.guess_type(filepath)[0]
				if not mimetype:
					mimetype = 'application/octet-stream'
				response = HttpResponse(download.read(), mimetype = mimetype)
				response['Content-Disposition'] = 'attachment; filename="icon.png"'
				return response
			except IOError:
				return render(request, 'error.html', {'error': 'Unable to open the file'})
			except:
				return render(request, 'error.html', {'error': 'Unexpected error'})
	return render(request, 'error.html', {'error': 'The file does not exist'})

def backup(obj):
	# Flag an existing object as a backup
	obj.BACKUP = True
	obj.save()

def show_list(request):
	# Refresh and serve up the list of plugins
	pluginlist = reload_list()
	response = HttpResponse(mimetype='text/html')
	response.write(pluginlist)
	return response

def read_config(location):
	# Read a plugin's configuration file
	lookhere = location + '/__init__.py'
	import imp
	f = open(lookhere)
	data = imp.load_source('data', '', f)
	f.close()
	return data
