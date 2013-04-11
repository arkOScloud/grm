from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
		url(r'^$', 'main.views.index', name='index'),
		url(r'^upload/$', 'main.views.upload', name='upload'),
		url(r'^file/(?P<filename>(.+))$', 'main.views.file', name='file'),
)
