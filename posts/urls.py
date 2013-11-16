from django.conf.urls import patterns, include, url

urlpatterns = patterns('posts.views',
    url(r'^$', 'homepage', name='home'),
    url(r'^add/news/$', 'add_news', name='add_news'),
    url(r'^edit/news/(?P<id>\d+)/$', 'edit_news', name='edit_news'),
    url(r'^posts/draft/$', 'view_posts_draft', name='posts_draft'),
    url(r'^posts/pending/$', 'view_posts_pending', name='posts_pending'),
    url(r'^posts/propose/(?P<post_id>\d+)/$', 'post_propose',
        name='post_propose'),

    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/$', 'view_post',
        name='post_view'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/revision/(?P<revision>\d+)/$', 'view_post',
        name='post_revision'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/revision/(?P<revision>\d+)/select/$', 'select_revision',
        name='post_revision_select'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/revision/(?P<revision>\d+)/delete/$', 'delete_revision',
        name='post_revision_delete'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/revisions/$', 'view_revisions',
        name='post_revisions'),
)