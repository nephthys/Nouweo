from django.conf.urls import patterns, include, url

urlpatterns = patterns('community.views',
	url(r'^users/(?P<id>\d+)/$', 'view_user_profile', name='user_profile'),
    url(r'^rating/(?P<model>post|idea|comment)/(?P<id>\d+)/(?P<direction>up|down)/$', 'add_vote',
        name='add_vote'),
	url(r'^comments/posted/$', 'comment_posted'),
    url(r'^comments/', include('django.contrib.comments.urls')),
)