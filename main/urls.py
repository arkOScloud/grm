from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
		url(r'^$', 'index', name='index'),
		url(r'^list/(?P<distro>(.+))$', 'show_list', name='plugins'),
		url(r'^upload/$', 'upload', name='upload'),
		url(r'^plugin/(?P<id>(.+))$', 'file', name='file'),
		url(r'^themes/$', 'show_themes', name='themes'),
		url(r'^theme/(?P<id>(.+))$', 'theme', name='theme'),
		url(r'^theme/$', 'upload_theme', name='upload')
)
