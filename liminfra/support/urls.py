from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
	url(r'^$', 'liminfra.support.views.overview', name='overview'),
	url(r'^create_ticket/$', 'liminfra.support.views.create_ticket', name='create-ticket'),
	url(r'^ticket/(?P<id>\d+)/$', 'liminfra.support.views.view_ticket', name='view-ticket'),
)
