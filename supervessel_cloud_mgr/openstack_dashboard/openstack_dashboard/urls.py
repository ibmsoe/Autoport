# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
URL patterns for the OpenStack Dashboard.
"""

from django.conf import settings
from django.conf.urls import include  # noqa
from django.conf.urls import patterns
from django.conf.urls.static import static  # noqa
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # noqa
from openstack_dashboard import views
from restful import urls as api_urls

import horizon
from openstack_dashboard.views import CheckCapiView

urlpatterns = patterns('',
    url(r'^$', 'openstack_dashboard.views.splash', name='splash'),
    url(r'^api/', include(api_urls), name='api'),
    url(r'^auth/', include('openstack_auth.urls')),
    url(r'^pointrate$', views.PointsRateJsonView.as_view(), name='pointrate'),
    url(r'^get_user_points$', views.UserPointsJsonView.as_view(), name='get_user_points'),
    url(r'^get_resource_count$', views.ResourceCountJsonView.as_view(), name='get_resource_count'),
    url(r'^get_accelerator_info$', views.AcceleratorInfoJsonView.as_view(), name='get_accelerator_info'),
    url(r'^image_list$', views.ImageListJsonView.as_view(), name='image_list'),
    url(r'^flavor_list$', views.FlavorsBySourceTypeJsonView.as_view(), name='flavor_list'),
    url(r'^set_language/', 'openstack_dashboard.views.set_language', name='set_language'),
    url(r'^vpn_account$', views.VPNAccountView.as_view(), name='vpn_account'),
    url(r'^notification$', views.NotificationView.as_view(), name='notification'),
    url(r'^notify_count$', views.NofityCountJsonView.as_view(), name='notify_count'),
    url(r'^check_capi$', CheckCapiView.as_view(), name='check_capi'),
    url(r'', include(horizon.urls))
)

# Development static app and project media serving using the staticfiles app.
urlpatterns += staticfiles_urlpatterns()

# Convenience function for serving user-uploaded media during
# development. Only active if DEBUG==True and the URL prefix is a local
# path. Production media should NOT be served by Django.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^500/$', 'django.views.defaults.server_error')
    )