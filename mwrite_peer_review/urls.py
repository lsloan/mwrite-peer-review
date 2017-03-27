"""mwrite_peer_review URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.http import Http404
import djangolti.views
from peer_review.views.special import FixedHttpProxy, LtiProxyView, DebugLtiParamsView
import peer_review.views.core as views


def not_found(request):
    raise Http404

urlpatterns = [
    url(r'^favicon.ico$', not_found),
    url(r'^unauthorized', views.UnauthorizedView.as_view(), name='unauthorized'),
    url(r'^launch', djangolti.views.LaunchView.as_view(), name='launch'),
    url(r'^(?P<url>health)$', FixedHttpProxy.as_view(base_url=settings.MWRITE_PEER_REVIEW_LEGACY_URL)),
    url(r'^(?P<url>.*)$', LtiProxyView.as_view(base_url=settings.MWRITE_PEER_REVIEW_LEGACY_URL))
]

if settings.DEBUG:
    from django.contrib.auth.views import login as auth_login
    debug_patterns = [
        url(r'^accounts/login/$', auth_login, name='login'),
        url(r'^debug/lti$', DebugLtiParamsView.as_view())
    ]
    urlpatterns = debug_patterns + urlpatterns
