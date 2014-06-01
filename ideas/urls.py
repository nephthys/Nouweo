from django.conf.urls import patterns, url
from .views import IdeaList, IdeaCreate, IdeaUpdate, IdeaDelete

urlpatterns = patterns('ideas.views',
    url(r'^$', IdeaList.as_view(), name='list_ideas'),
    url(r'^add/$', IdeaCreate.as_view(), name='add_idea'),
    url(r'^edit/(?P<pk>\d+)/$', IdeaUpdate.as_view(), name='edit_idea'),
    url(r'^delete/(?P<pk>\d+)/$', IdeaDelete.as_view(), name='delete_idea'),
)