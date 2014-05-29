from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('genesis_repo.views',
		url(r'^$', 'index', name='index'),
		url(r'^list/(?P<distro>(.+))$', 'show_list', name='plugins'),
		url(r'^upload/$', 'upload', name='upload'),
		url(r'^plugin/(?P<id>(.+))$', 'getplugin', name='getplugin'),
		url(r'^assets/(?P<id>(.+))$', 'assets', name='assets'),
		url(r'^themes/$', 'show_themes', name='themes'),
		url(r'^theme/(?P<id>(.+))$', 'theme', name='theme'),
		url(r'^theme/$', 'upload_theme', name='upload'),
		url(r'^accounts/', include('registration.backends.default.urls')),
		url(r'^admin/', include(admin.site.urls))
)
