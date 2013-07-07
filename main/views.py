import os
import subprocess
import mimetypes
import sys

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.core.files import File

from main.models import Plugin, Theme, SecretKey
from main.forms import PluginForm, ThemeForm

def reload_list(distro):
	pluginlist = []
	plugins = Plugin.objects.filter(BACKUP=False)
	for data in plugins:
		if distro in data.PLATFORMS or 'any' in data.PLATFORMS:
			entry = {'description': data.DESCRIPTION, 'author': data.AUTHOR, 'modules': data.MODULES, 'platforms': data.PLATFORMS, 'version': data.VERSION, 'deps': data.DEPS, 'icon': data.ICON, 'homepage': data.HOMEPAGE, 'id': data.PLUGIN_ID, 'name': data.name}
			pluginlist.append(entry)
	return pluginlist

def reload_themes():
	themelist = []
	themes = Theme.objects.all()
	for theme in themes:
		entry = {'description': theme.DESCRIPTION, 'author': theme.AUTHOR, 'version': theme.VERSION, 'homepage': theme.HOMEPAGE, 'id': theme.THEME_ID, 'name': theme.name}
		themelist.append(entry)
	return themelist

def index(request):
	return render(request, 'index.html')

def upload(request):
	if request.method == 'POST':
		form = PluginForm(request.POST, request.FILES)
		keys = SecretKey.objects.all()
		oldkey = ''

		if not form.is_valid():
			return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'Form not valid', 'type': 'alert-error'})

		if request.FILES['data_file'].content_type == 'application/gzip':
			# Check validity of provided secret key
			try:
				SecretKey.objects.get(key=request.POST['secret_key'])
			except:
				return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'Secret key incorrect', 'type': 'alert-error'})

			if SecretKey.objects.get(key=request.POST['secret_key']).admin == True:
				superkey = True
			else:
				superkey = False

			newfile = Plugin(name=request.FILES['data_file'].name, data_file=request.FILES['data_file'], secret_key=request.POST['secret_key'])
			newfile.save()

			file = Plugin.objects.get(name=request.FILES['data_file'].name)
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
				return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'Malformed archive. Please resubmit in accordance with Genesis Plugin API guidelines.', 'type': 'alert-error'})

			# If upgrading, check permission and backup old one if necessary
			if Plugin.objects.filter(PLUGIN_ID=directory, BACKUP=False).exists():
				condition = Plugin.objects.get(PLUGIN_ID=directory, BACKUP=False).secret_key
				if condition != SecretKey.objects.get(key=request.POST['secret_key']).key and superkey != True:
					newfile.delete()
					subprocess.call(['rm', '-r', temp + directory])
					return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'No permission to upgrade this plugin', 'type': 'alert-error'})
				else:
					oldkey = Plugin.objects.get(PLUGIN_ID=directory, BACKUP=False).secret_key
					backup(Plugin.objects.get(PLUGIN_ID=directory, BACKUP=False))

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
			file.ICON = data.ICON
			file.BACKUP = False
			if oldkey != '':
				file.secret_key = oldkey
			file.save()

			subprocess.call(['rm', '-r', temp + directory])

			# Display success message
			return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'Upload successful!', 'type': 'alert-success'})

		else:
			return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'File not of acceptable type', 'type': 'alert-error'})
	else:
		form = PluginForm()
	return render(request, 'upload.html', {'form': form, 'function': 'plugin'})

def upload_theme(request):
	if request.method == 'POST':
		form = ThemeForm(request.POST)
		keys = SecretKey.objects.all()

		if not form.is_valid():
			return render(request, 'upload.html', {'form': form, 'function': 'theme', 'message': 'Form not valid', 'type': 'alert-error'})

		try:
			SecretKey.objects.get(key=request.POST['secret_key'])
		except:
			return render(request, 'upload.html', {'form': form, 'function': 'theme', 'message': 'Secret key incorrect', 'type': 'alert-error'})

		newfile = Theme(name=request.POST['name'], THEME_ID=request.POST['THEME_ID'], 
			theme_css=request.POST['theme_css'], DESCRIPTION=request.POST['DESCRIPTION'], 
			AUTHOR=request.POST['AUTHOR'], VERSION=request.POST['VERSION'], 
			HOMEPAGE=request.POST['HOMEPAGE'], secret_key=request.POST['secret_key'])
		newfile.save()

		# Display success message
		return render(request, 'upload.html', {'form': form, 'function': 'theme', 'message': 'Upload successful!', 'type': 'alert-success'})
	else:
		form = ThemeForm()
	return render(request, 'upload.html', {'form': form, 'function': 'theme'})

def file(request, id):
	# Serve up the plugin archive file
	getfiles = Plugin.objects.filter(BACKUP=False)
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

def theme(request, id):
	# Serve up the theme name and CSS as tuple
	theme = Theme.objects.get(THEME_ID=id)
	data = theme.name, theme.theme_css 
	response = HttpResponse(mimetype='text/html')
	response.write(data)
	return response

def backup(obj):
	# Flag an existing object as a backup
	obj.BACKUP = True
	obj.save()

def show_list(request, distro):
	# Refresh and serve up the list of plugins
	pluginlist = reload_list(distro)
	response = HttpResponse(mimetype='text/html')
	response.write(pluginlist)
	return response

def show_themes(request):
	# Refresh and serve up the list of themes
	themelist = reload_themes()
	response = HttpResponse(mimetype='text/html')
	response.write(themelist)
	return response

def read_config(location):
	# Read a plugin's configuration file
	lookhere = location + '/__init__.py'
	import imp
	f = open(lookhere)
	data = imp.load_source('data', '', f)
	f.close()
	return data
