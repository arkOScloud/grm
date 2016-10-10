from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('grm.views',
    url(r'^$', 'index', name='index'),
    url(r'^upload', 'upload', name='upload'),
    url(r'^api/v1/apps$', 'apps', name='apps'),
    url(r'^api/v1/echo$', 'echo', name='echo'),
    url(r'^api/v1/apps/(?P<id>(.+))$', 'apps', name='apps'),
    url(r'^api/v1/error$', 'error', name='error'),
    url(r'^api/v1/updates/(?P<id>(.+))$', 'updates', name='updates'),
    url(r'^api/v1/assets/(?P<id>(.+))$', 'assets', name='assets'),
    url(r'^api/v1/signatures/(?P<id>(.+))$', 'signatures', name='signatures'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls))
)
