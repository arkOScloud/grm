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

def reload_list():
	pluginlist = []
	plugins = Plugin.objects.filter(BACKUP=False)
	for data in plugins:
		entry = {'atype': data.TYPE, 'description': data.DESCRIPTION, 
		'author': data.AUTHOR, 'modules': json.loads(data.MODULES), 
		'version': data.VERSION, 'deps': json.loads(data.DEPS), 'icon': data.ICON, 
		'homepage': data.HOMEPAGE, 'id': data.PLUGIN_ID,
		'app_author': data.APP_AUTHOR, 'app_homepage': data.APP_HOMEPAGE,
		'assets': data.LOGO != '', 'long_description': data.LONG_DESCRIPTION,
		'name': data.name, 'categories': json.loads(data.CATEGORIES)}
		pluginlist.append(entry)
	return pluginlist

def index(request):
	return render(request, 'index.html')

@csrf_exempt
@login_required
def upload(request):
	if request.method == 'POST':
		form = PluginForm(request.POST, request.FILES)
		if not request.FILES['data_file'].content_type in ['application/gzip', 'application/x-gzip']:
			return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'File not of acceptable type', 'type': 'alert-danger'})
		else:
			arch = request.FILES['data_file']
			arch = cStringIO.StringIO(arch.read())
			t = tarfile.open(fileobj=arch)

			data = None
			for x in t.getmembers():
				if 'manifest.json' in x.name:
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

def apps(request, id=""):
	if request.method == "POST":
	    return redirect("genesis_repo.views.upload")
    if id:
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
    	return HttpResponse(json.dumps(a), content_type='application/json')
    else:
        return redirect("genesis_repo.views.show_list")

def assets(request, id):
	try:
		p = Plugin.objects.get(PLUGIN_ID=id, BACKUP=False)
		a = {'status': 200, 'info': p.PLUGIN_ID, 'logo': p.LOGO if hasattr(p, 'LOGO') else None, 'screenshots': [x.image for x in p.screens.all()]}
	except Plugin.DoesNotExist:
		a = {'status': 404, 'info': 'No plugin found with that id.'}
	return HttpResponse(json.dumps(a), content_type='application/json')

@csrf_exempt
def error(request):
    if request.method == "POST":
        data = json.loads(request.body)
    	try:
    	    if CrashReport.objects.filter(summary=data["summary"]):
        		a = {'status': 200, 'info': 'Your crash report was submitted successfully.'}
                return HttpResponse(json.dumps(a), content_type='application/json')
    		c = CrashReport(trace=data["trace"], version=data["version"], 
    		    arch=data["arch"])
    		c.save()
    		a = {'status': 200, 'info': 'Your crash report was submitted successfully.'}
    	except:
    		a = {'status': 500, 'info': 'An unspecified server error occurred and your crash report couldn\'t be submitted. Please submit manually to the developers!'}
	a = {'status': 400, 'info': 'Can only POST to this resource'}
	return HttpResponse(json.dumps(a), content_type='application/json')

def backup(obj):
	# Flag an existing object as a backup
	obj.BACKUP = True
	obj.save()

def show_list(request, distro):
	# Refresh and serve up the list of plugins
	pluginlist = reload_list()
	return HttpResponse(json.dumps(pluginlist), content_type='application/json')
