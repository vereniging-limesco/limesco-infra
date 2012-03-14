from django.conf.urls.defaults import patterns, include, url
from liminfra import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Dit kan je beter door je webserver laten doen. Die is daar beter in.
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

if settings.DEBUG or 'liminfra.memberadmin' in settings.INSTALLED_APPS:
	urlpatterns += patterns('',
		url(r'^admin/', include(admin.site.urls)),
	)

if 'liminfra.memberadmin' in settings.INSTALLED_APPS and 'liminfra.portal' not in settings.INSTALLED_APPS:
	urlpatterns += patterns('', url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/admin/'}))

if 'liminfra.portal' in settings.INSTALLED_APPS:
	urlpatterns += patterns('',
		url(r'^$', 'liminfra.portal.views.welcome', name='welcome'),
		url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
		url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
	)
if 'liminfra.support' in settings.INSTALLED_APPS:
	urlpatterns += patterns('',
		url(r'^support/', include('liminfra.support.urls')),
	)
