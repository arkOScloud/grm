import cStringIO
import hashlib
import json
import os
import random
import tarfile
import subprocess
import sys

from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError

from models import Plugin, Theme, Image, CrashReport, Update
from forms import PluginForm, ThemeForm


def reload_list():
    pluginlist = []
    plugins = Plugin.objects.filter(BACKUP=False)
    for data in plugins:
        try:
            logo = data.images.get(itype='logo').id
        except ObjectDoesNotExist:
            logo = None
        try:
            screens = [x.id for x in data.images.filter(itype="screenshot")]
        except ObjectDoesNotExist:
            screens = []
        entry = {'id': data.PLUGIN_ID, 'name': data.name, 'type': data.TYPE, 'icon': data.ICON, 
        'description': {'short': data.DESCRIPTION, 'long': data.LONG_DESCRIPTION},
        'categories': json.loads(data.CATEGORIES), 'version': data.VERSION, 
        'author': data.AUTHOR, 'homepage': data.HOMEPAGE, 
        'app_author': data.APP_AUTHOR, 'app_homepage': data.APP_HOMEPAGE, 
        'assets': {'logo': logo, 'screens': screens}, 'modules': json.loads(data.MODULES), 
        'dependencies': json.loads(data.DEPS)}
        pluginlist.append(entry)
    return pluginlist

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@login_required
def upload(request):
    if request.method == 'POST':
        form = PluginForm(request.POST, request.FILES)
        if not request.FILES['archive'].content_type in ['application/gzip', 'application/x-gzip']:
            return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'File not of acceptable type', 'type': 'alert-danger'})
        else:
            arch = request.FILES['archive']
            arch = cStringIO.StringIO(arch.read())
            t = tarfile.open(fileobj=arch)

            data = None
            for x in t.getmembers():
                if '/manifest.json' in x.name:
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
                archive=request.FILES['archive'],
                TYPE=data['type'],
                DESCRIPTION=data['description']['short'],
                LONG_DESCRIPTION=data['description'].get('long', ''),
                AUTHOR=data['author'],
                HOMEPAGE=data['homepage'],
                APP_AUTHOR=data.get('app_author', ''),
                APP_HOMEPAGE=data.get('app_homepage', ''),
                MODULES=json.dumps(data['modules']),
                CATEGORIES=json.dumps(data['categories']),
                VERSION=data['version'],
                DEPS=json.dumps(data['dependencies']),
                PLUGIN_ID=pid,
                ICON=data['icon'],
                BACKUP=False
                )
            f.save()
            if data.get('logo'):
                s = Image(itype="logo", plugin=f)
                s.image.save("logo.png", t.extractfile(os.path.join(pid, 'assets/logo.png')))
                s.save()
            if data.get('screenshots'):
                for x in data['screenshots']:
                    s = Image(itype="screenshot", plugin=f)
                    s.image.save("screen.jpg", t.extractfile(os.path.join(pid, 'assets', x)))
                    s.save()
            # Display success message
            return render(request, 'upload.html', {'form': form, 'function': 'plugin', 'message': 'Upload successful!', 'type': 'alert-success'})
    else:
        form = PluginForm()
    return render(request, 'upload.html', {'form': form, 'function': 'plugin'})

def apps(request, id=""):
    if id:
        try:
            p = Plugin.objects.get(PLUGIN_ID=id, BACKUP=False)
            if os.path.basename(p.PLUGIN_ID) == id:
                try:
                    with open(p.archive.path, 'r') as f:
                        data = f.read()
                    return HttpResponse(data, content_type='application/gzip')
                except IOError:
                    return HttpResponseServerError(json.dumps({'message': 'Unable to open the file'}), content_type='application/json')
                except:
                    return HttpResponseServerError(json.dumps({'message': 'Unexpected error'}), content_type='application/json')
        except Plugin.DoesNotExist:
            return HttpResponseNotFound(json.dumps({'message': 'No plugin found with that id.'}), content_type='application/json')
    else:
        return show_list(request)

def assets(request, id):
    try:
        p = Image.objects.get(pk=id)
        with open(p.image.path, 'r') as f:
            return HttpResponse(f.read(), content_type='image/jpeg' if p.itype == 'screenshot' else 'image/png')
    except Plugin.DoesNotExist:
        return HttpResponseNotFound(json.dumps({'message': 'No assets found with that id.'}), content_type='application/json')

def signatures(request, id):
    id = int(id)
    try:
        s = Update.objects.get(pk=id)
        return HttpResponse(s.signature.sig)
    except Update.DoesNotExist:
        return HttpResponseNotFound(json.dumps({'message': 'No signature found with that id'}))

def updates(request, id):
    if not id:
        id = 0
    id = int(id)
    ujson = []
    upds = Update.objects.filter(pk__gt=id)
    for upd in upds:
        ujson.append({"id": upd.pk, "name": upd.name, "info": upd.info, 
            "date": upd.created_at.isoformat(), "tasks": upd.tasks})
    return HttpResponse(json.dumps({"updates": ujson}))

@csrf_exempt
def error(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            if CrashReport.objects.filter(summary=data["summary"]):
                return HttpResponse(json.dumps({'message': 'Your crash report has already been submitted. Developers will take care of it as soon as possible.'}), content_type='application/json')
            c = CrashReport(summary=data["summary"], trace=data["trace"], 
                version=data["version"], arch=data["arch"], report=data["report"])
            c.save()
            return HttpResponse(json.dumps({'message': 'Your crash report was submitted successfully.'}), content_type='application/json')
        except:
            return HttpResponseServerError(json.dumps({'message': 'An unspecified server error occurred and your crash report couldn\'t be submitted. Please submit manually to the developers!'}), content_type='application/json')
    return HttpResponseBadRequest(json.dumps({'message': 'Can only POST to this resource'}), content_type='application/json')

def backup(obj):
    # Flag an existing object as a backup
    obj.BACKUP = True
    obj.save()

def show_list(request):
    # Refresh and serve up the list of plugins
    pluginlist = reload_list()
    return HttpResponse(json.dumps({"applications": pluginlist}), content_type='application/json')
