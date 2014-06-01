from django.conf.urls import patterns, include

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ('^admin/', include(admin.site.urls)),
    ('^', include('community.urls')),
    ('^ideas/', include('ideas.urls')),
    ('^', include('posts.urls')),
)
