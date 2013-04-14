from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
		url(r'^$', 'index', name='index'),
		url(r'^upload/$', 'upload', name='upload'),
		url(r'^list', 'show_list', name='plugins'),
		url(r'^plugin/(?P<id>(.+))$', 'file', name='file'),
		url(r'^icon/(?P<id>(.+))$', 'icon', name='icon')
)
