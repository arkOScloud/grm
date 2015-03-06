import base64
import cStringIO
import json
import os
import tarfile
import subprocess
import sys

from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.core.files import File

from models import Plugin, Theme, Screenshot, CrashReport
from forms import PluginForm, ThemeForm

def reload_list(distro):
	pluginlist = []
	plugins = Plugin.objects.filter(BACKUP=False)
	for data in plugins:
		platforms = json.loads(data.PLATFORMS)
		if distro in platforms or 'any' in platforms:
			entry = {'ptype': data.TYPE, 'description': data.DESCRIPTION, 
			'author': data.AUTHOR, 'modules': json.loads(data.MODULES), 
			'platforms': platforms, 'version': data.VERSION, 
			'deps': json.loads(data.DEPS), 'icon': data.ICON, 
			'homepage': data.HOMEPAGE, 'id': data.PLUGIN_ID,
			'app_author': data.APP_AUTHOR, 'app_homepage': data.APP_HOMEPAGE,
			'assets': data.LOGO != '', 'long_description': data.LONG_DESCRIPTION,
			'name': data.name, 'categories': json.loads(data.CATEGORIES)}
			pluginlist.append(entry)
	return pluginlist

def reload_themes():
	themelist = []
	themes = Theme.objects.all()
	for theme in themes:
		entry = {'description': theme.DESCRIPTION, 'author': theme.AUTHOR, 
		'version': theme.VERSION, 'homepage': theme.HOMEPAGE, 
		'id': theme.THEME_ID, 'name': theme.name}
		themelist.append(entry)
	return themelist

@csrf_exempt
def index(request):
	if request.method == 'POST' and 'application/json' in request.META.get('CONTENT_TYPE'):
		data = json.loads(request.body)
		if data.has_key('get') and data['get'] == 'list':
			return show_list(request, data['distro'])
		elif data.has_key('get') and data['get'] == 'plugin':
			return getplugin(request, data['id'])
		elif data.has_key('get') and data['get'] == 'assets':
			return assets(request, data['id'])
		elif data.has_key('put') and data['put'] == 'crashreport':
			return crashreport(request, data['report'], data['comments'])
		else:
			get_reqno()
			return HttpResponse(json.dumps({'status': 400, 'info': 'Malformed request'}), content_type='application/json')
	return render(request, 'index.html', {'reqno': get_reqno(False)})

@login_required
def upload(request):
	if request.method == 'POST':
		form = PluginForm(request.POST, request.FILES)
		if not request.FILES['data_file'].content_type in ['application/gzip', 'application/x-gzip']:
			return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'File not of acceptable type', 'type': 'alert-danger'})
		else:
			get_reqno()
			arch = request.FILES['data_file']
			arch = cStringIO.StringIO(arch.read())
			t = tarfile.open(fileobj=arch)

			data = None
			for x in t.getmembers():
				if '/plugin.json' in x.name:
					pid = x.name.split('/')[0]
					data = json.loads(t.extractfile(x).read())
			if not data:
				return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'Malformed archive. Please resubmit in accordance with Genesis Plugin API guidelines.', 'type': 'alert-error'})

			# If upgrading, check permission and backup old one if necessary
			if Plugin.objects.filter(PLUGIN_ID=pid, BACKUP=False).exists():
				backup(Plugin.objects.get(PLUGIN_ID=pid, BACKUP=False))

			# Update the database with the new plugin data
			f = Plugin(
				name=data['name'],
				data_file=request.FILES['data_file'],
				TYPE=data['type'],
				DESCRIPTION=data['description']['short'],
				LONG_DESCRIPTION=data['description']['long'] if data['description'].has_key('long') else '',
				AUTHOR=data['author'],
				HOMEPAGE=data['homepage'],
				APP_AUTHOR=data['app_author'] if data.has_key('app_author') else '',
				APP_HOMEPAGE=data['app_homepage'] if data.has_key('app_homepage') else '',
				MODULES=json.dumps(data['modules']),
				PLATFORMS=json.dumps(data['platforms']),
				CATEGORIES=json.dumps(data['categories']),
				VERSION=data['version'],
				DEPS=json.dumps(data['dependencies']),
				PLUGIN_ID=pid,
				ICON=data['icon'],
				LOGO=base64.b64encode(t.extractfile(os.path.join(pid, 'files/logo.png')).read()) if data.has_key('logo') and data['logo'] else '',
				BACKUP=False
				)
			f.save()
			if data.has_key('screenshots') and data['screenshots']:
				for x in data['screenshots']:
					b = base64.b64encode(t.extractfile(os.path.join(pid, 'files', x)).read())
					s = Screenshot(plugin=f, image=b)
					s.save()

			# Display success message
			return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'Upload successful!', 'type': 'alert-success'})
	else:
		form = PluginForm()
	return render(request, 'upload.html', {'form': form, 'function': 'plugin'})

def upload_theme(request):
	if request.method == 'POST':
		form = ThemeForm(request.POST)

		if not form.is_valid():
			return render(request, 'upload.html', {'form': form, 'function': 'theme', 'message': 'Form not valid', 'type': 'alert-danger'})

		get_reqno()
		newfile = Theme(name=request.POST['name'], THEME_ID=request.POST['THEME_ID'], 
			theme_css=request.POST['theme_css'], DESCRIPTION=request.POST['DESCRIPTION'], 
			AUTHOR=request.POST['AUTHOR'], VERSION=request.POST['VERSION'], 
			HOMEPAGE=request.POST['HOMEPAGE'])
		newfile.save()

		# Display success message
		return render(request, 'upload.html', {'form': form, 'function': 'theme', 'message': 'Upload successful!', 'type': 'alert-success'})
	else:
		form = ThemeForm()
	return render(request, 'upload.html', {'form': form, 'function': 'theme'})

def getplugin(request, id):
	# Serve up the plugin archive file
	try:
		p = Plugin.objects.get(PLUGIN_ID=id, BACKUP=False)
		if os.path.basename(p.PLUGIN_ID) == id:
			try:
				filepath = os.path.join(settings.MEDIA_ROOT, p.data_file.url)
				f = open(filepath, 'r')
				data = base64.b64encode(f.read())
				f.close()
				a = {'status': 200, 'info': data}
			except IOError:
				a = {'status': 500, 'info': 'Unable to open the file'}
			except:
				a = {'status': 500, 'info': 'Unexpected error'}
	except Plugin.DoesNotExist:
		a = {'status': 404, 'info': 'No plugin found with that id.'}
	get_reqno()
	return HttpResponse(json.dumps(a), content_type='application/json')

def assets(request, id):
	try:
		p = Plugin.objects.get(PLUGIN_ID=id, BACKUP=False)
		a = {'status': 200, 'info': p.PLUGIN_ID, 'logo': p.LOGO if hasattr(p, 'LOGO') else None, 'screenshots': [x.image for x in p.screens.all()]}
	except Plugin.DoesNotExist:
		a = {'status': 404, 'info': 'No plugin found with that id.'}
	get_reqno()
	return HttpResponse(json.dumps(a), content_type='application/json')

def crashreport(request, cr, co):
	try:
		c = CrashReport(report=cr, comments=co)
		c.save()
		get_reqno()
		a = {'status': 200, 'info': 'Your crash report was submitted successfully.'}
	except:
		a = {'status': 500, 'info': 'An unspecified server error occurred and your crash report couldn\'t be submitted. Please submit manually to the developers!'}
	return HttpResponse(json.dumps(a), content_type='application/json')

def theme(request, id):
	# Serve up the theme name and CSS as tuple
	theme = Theme.objects.get(THEME_ID=id)
	data = theme.name, theme.theme_css 
	response = HttpResponse(mimetype='text/html')
	response.write(data)
	get_reqno()
	return response

def backup(obj):
	# Flag an existing object as a backup
	obj.BACKUP = True
	obj.save()

def show_list(request, distro):
	# Refresh and serve up the list of plugins
	get_reqno()
	pluginlist = reload_list(distro)
	return HttpResponse(json.dumps(pluginlist), content_type='application/json')

def show_themes(request):
	# Refresh and serve up the list of themes
	themelist = reload_themes()
	response = HttpResponse(mimetype='text/html')
	response.write(themelist)
	get_reqno()
	return response

def get_reqno(incr=True):
	if not cache.get('reqno'):
		cache.set('reqno', 0, None)
	if incr:
		cache.set('reqno', cache.get('reqno') + 1, None)
	return cache.get('reqno')
