from django.conf.urls import patterns, include, url
from .views import PostHomepage, PostCreateNews, PostUpdate, PostDetail, \
    PostDetailRevisions, PostSelectRevision, PostDeleteRevision, PostDelete, \
    PostDraft, PostPending

urlpatterns = patterns('posts.views',
    url(r'^$', PostHomepage.as_view(), name='home'),
    url(r'^posts/add_news/$', PostCreateNews.as_view(), name='add_news'),
    url(r'^posts/edit/(?P<pk>\d+)/$', PostUpdate.as_view(), name='edit_post'),
    url(r'^posts/delete/(?P<pk>\d+)/$', PostDelete.as_view(), name='delete_post'),
    url(r'^posts/draft/$', PostDraft.as_view(), name='posts_draft'),
    url(r'^posts/pending/$', PostPending.as_view(), name='posts_pending'),
    url(r'^posts/propose/(?P<post_id>\d+)/$', 'post_propose',
        name='post_propose'),

    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/$', PostDetail.as_view(),
        name='post_view'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/revision/(?P<revision>\d+)/$', PostDetail.as_view(),
        name='post_revision'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/revision/(?P<revision>\d+)/select/$', PostSelectRevision.as_view(),
        name='post_revision_select'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/revision/(?P<revision>\d+)/delete/$', PostDeleteRevision.as_view(),
        name='post_revision_delete'),
    url(r'^(?P<cat>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/revisions/$', 
        PostDetailRevisions.as_view(), name='post_revisions'),
)