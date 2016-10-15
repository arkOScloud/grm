import cStringIO
import json
import os
import tarfile
import requests

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    JsonResponse, HttpResponse, HttpResponseRedirect,
    HttpResponsePermanentRedirect
)

from models import Plugin, Image, CrashReport, Update
from forms import PluginForm


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
        pluginlist.append({
            'id': data.PLUGIN_ID, 'name': data.name, 'type': data.TYPE,
            'icon': data.ICON, 'description': {
                'short': data.DESCRIPTION, 'long': data.LONG_DESCRIPTION
            }, 'categories': json.loads(data.CATEGORIES),
            'version': data.VERSION, 'author': data.AUTHOR,
            'homepage': data.HOMEPAGE, 'app_author': data.APP_AUTHOR,
            'app_homepage': data.APP_HOMEPAGE, 'assets': {
                'logo': logo, 'screens': screens
            }, 'modules': json.loads(data.MODULES),
            'dependencies': json.loads(data.DEPS)
        })
    return pluginlist


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def echo(request):
    ip = request.META.get('HTTP_X_REAL_IP')
    id = request.POST.get('id')
    uri = request.POST.get('uri')
    port = request.POST.get('port')

    if not id and not port:
        return JsonResponse({"ip": ip})
    if not uri:
        uri = ip

    try:
        requests.post('http://' + uri + ':' + port + '/' + id, timeout=5.0)
        outbound_ok = True
    except:
        outbound_ok = False
    return JsonResponse({"ip": ip, "outbound_ok": outbound_ok})


@csrf_exempt
@login_required
def upload(request):
    if request.method == 'POST':
        form = PluginForm(request.POST, request.FILES)
        if not request.FILES['archive'].content_type in \
                ['application/gzip', 'application/x-gzip']:
            return render(
                request, 'upload.html', {
                    'form': form, 'function': 'plugin',
                    'message': 'File not of acceptable type',
                    'type': 'alert-danger'
                })
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
                return render(
                    request, 'upload.html', {
                        'form': form, 'function': 'plugin',
                        'message': 'Malformed archive. Please resubmit in '
                        'accordance with Genesis Plugin API guidelines.',
                        'type': 'alert-error'
                    })

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
                s.image.save(
                    "logo.png",
                    t.extractfile(os.path.join(pid, 'assets/logo.png')))
                s.save()
            if data.get('screenshots'):
                for x in data['screenshots']:
                    s = Image(itype="screenshot", plugin=f)
                    s.image.save(
                        "screen.jpg",
                        t.extractfile(os.path.join(pid, 'assets', x)))
                    s.save()
            # Display success message
            return render(
                request, 'upload.html', {
                    'form': form, 'function': 'plugin',
                    'message': 'Upload successful!', 'type': 'alert-success'
                })
    else:
        form = PluginForm()
    return render(request, 'upload.html', {'form': form, 'function': 'plugin'})


def apps(request, id=""):
    if id:
        try:
            p = Plugin.objects.get(PLUGIN_ID=id, BACKUP=False)
            if os.path.basename(p.PLUGIN_ID) == id:
                try:
                    p.downloads += 1
                    p.save()
                except:
                    pass
                try:
                    basename = os.path.basename(p.archive.path)
                    return HttpResponseRedirect("/media/{0}".format(basename))
                except:
                    return JsonResponse(
                        {'message': 'Unexpected error'}, status=500)
        except Plugin.DoesNotExist:
            return JsonResponse(
                {'message': 'No plugin found with that id.'}, status=404)
    else:
        return show_list(request)


def assets(request, id):
    try:
        p = Image.objects.get(pk=id)
        basename = os.path.basename(p.image.path)
        return HttpResponsePermanentRedirect("/media/{0}".format(basename))
    except Image.DoesNotExist:
        return JsonResponse(
            {'message': 'No assets found with that id.'}, status=404)


def signatures(request, id):
    id = int(id)
    try:
        s = Update.objects.get(pk=id)
        return HttpResponse(s.signature.sig)
    except Update.DoesNotExist:
        return JsonResponse(
            {'message': 'No signature found with that id'}, status=404)


def updates(request, id):
    if not id:
        id = 0
    id = int(id)
    ujson = []
    upds = Update.objects.filter(pk__gt=id)
    for upd in upds:
        ujson.append({
            "id": upd.pk, "name": upd.name, "info": upd.info,
            "date": upd.created_at.isoformat(), "tasks": upd.tasks})
    return JsonResponse({"updates": ujson})


@csrf_exempt
def error(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            if CrashReport.objects.filter(summary=data["summary"]):
                return JsonResponse({
                    'message': 'Your crash report has already been submitted.'
                    ' Developers will take care of it as soon as possible.'})
            c = CrashReport(
                summary=data["summary"], trace=data["trace"],
                version=data["version"], arch=data["arch"],
                report=data["report"])
            c.save()
            return JsonResponse({
                'message': 'Your crash report was submitted successfully.'})
        except:
            return JsonResponse({
                'message': 'An unspecified server error occurred and your '
                'crash report couldn\'t be submitted. Please submit manually '
                'to the developers!'},
                status='500')
    return JsonResponse({})


def backup(obj):
    # Flag an existing object as a backup
    obj.BACKUP = True
    obj.save()


def show_list(request):
    # Refresh and serve up the list of plugins
    pluginlist = reload_list()
    return JsonResponse({"applications": pluginlist})
