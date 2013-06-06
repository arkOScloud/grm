from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
		url(r'^$', 'index', name='index'),
		url(r'^upload/$', 'upload', name='upload'),
		url(r'^list/(?P<distro>(.+))$', 'show_list', name='plugins'),
		url(r'^webapps/$', 'show_webapps', name='webapps'),
		url(r'^themes/$', 'show_themes', name='themes'),
		url(r'^themes/(?P<id>(.+))$', 'theme', name='theme'),
		url(r'^plugin/(?P<id>(.+))$', 'file', name='file')
)
