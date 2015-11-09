from django.conf.urls import patterns, url
from openstack_dashboard.restful.user_views import UserViewSet

__author__ = 'yuehaitao'

user_api = UserViewSet.as_view({
    'post': 'register',
    'put': 'update_password',
})

urlpatterns = patterns('',
    url(r'^user$', user_api, name="user"),
)
