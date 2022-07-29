from django.urls import re_path
from blog import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [

    # re_path(r'^$', views.PostListView.as_view(), name='post_list'),
    re_path(r'^$', views.post_list, name='post_list'),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'r'(?P<post>[-\w]+)/$',
            views.post_detail, name='post_detail'),
    re_path(r'^tag/(?P<tag_slug>[-\w]+)/$', views.post_list, name='post_list_by_tag'),
    re_path(r'^tag/(?P<search>[-\w]+)/$', views.post_list, name='post_list_by_search'),
    re_path(r'^(?P<post_id>\d+)/share/$', views.post_share, name='post_share'),
    # re_path(r'^login/$', views.user_login, name='login'),
    re_path(r'^logout/$',  LogoutView.as_view(template_name='blog/account/registration/logged_out.html'),
            name='logout'),
    re_path(r'^register/$', views.register, name='register'),
    re_path(r'^search/$', views.post_search, name='post_search'),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'r'(?P<post>[-\w]+)/addlike/$', views.add_like,
            name='add_like'),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'r'(?P<post>[-\w]+)/adddislike/$',
            views.add_dislike, name='add_dislike'),

]
