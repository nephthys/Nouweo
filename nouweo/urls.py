from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from posts.views import *

urlpatterns = patterns('',
    url(r'^$', homepage, name='home'),
    url(r'^add/news/$', add_news, name='add_news'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/$', view_post, 
        name='post_view'),
    url(r'^admin/', include(admin.site.urls)),
    ('^', include('mezzanine.urls')),
)
