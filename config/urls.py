from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # Examples:

    # url(r'^$', 'views.index', name='index'),
    url(r'^admin/', include(admin.site.urls)),

);
