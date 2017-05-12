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
from peer_review.views.core import *
from peer_review.views.special import FixedHttpProxy, LtiProxyView, DebugLtiParamsView, SafariLaunchPopup


def not_found(request):
    raise Http404

urlpatterns = [
    url(r'^$', IndexView.as_view()),
    url(r'^favicon.ico$', not_found),
    url(r'^launch$', djangolti.views.LaunchView.as_view(), name='launch'),
    url(r'^dashboard/instructor$', InstructorDashboardView.as_view()),
    url(r'^dashboard/student$', StudentDashboardView.as_view()),
    url(r'^review/rubric/(?P<rubric_id>[0-9]+)/all$', ReviewsByStudentView.as_view()),
    url(r'^rubric/course/(?P<course_id>[0-9]+)/assignment/(?P<assignment_id>[0-9]+)$', RubricCreationFormView.as_view()),
    url(r'^review/submission/(?P<submission_id>[0-9]+)$', PeerReviewView.as_view()),
    url(r'^review/submission/(?P<submission_id>[0-9]+)/completed$', ReviewsOfMyWorkView.as_view()),
    url(r'^review/student/(?P<student_id>[0-9]+)/rubric/(?P<rubric_id>[0-9]+)$', ReviewsForAStudentView.as_view()),
    url(r'^safari$', SafariLaunchPopup.as_view()),
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
