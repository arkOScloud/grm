from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
		url(r'^$', 'main.views.index', name='index'),
		url(r'^upload/$', 'main.views.upload', name='upload'),
		url(r'^list', 'main.views.show_list', name='plugins'),
		url(r'^plugin/(?P<id>(.+))$', 'main.views.file', name='file'),
		url(r'^icon/(?P<id>(.+))$', 'main.views.icon', name='icon')
)
