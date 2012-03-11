from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from liminfra.settings import MEDIA_ROOT

urlpatterns = patterns('',
	url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
	url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

	url(r'^admin/', include(admin.site.urls)),

	# Dit kan je beter door je webserver laten doen. Die is daar beter in.
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)
