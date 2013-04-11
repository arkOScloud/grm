from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
		url(r'^$', 'main.views.index', name='index'),
		url(r'^upload/$', 'main.views.upload', name='upload'),
		url(r'^plugins', 'main.views.show_list', name='plugins'),
		url(r'^file/(?P<filename>(.+))$', 'main.views.file', name='file'),
)
