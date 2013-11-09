from django.conf.urls import patterns, include

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ('^admin/', include(admin.site.urls)),
    ('^', include('community.urls')),
    ('^', include('posts.urls')),
)
