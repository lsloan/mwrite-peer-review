from django.http import Http404
from django.conf import settings
from django.conf.urls import url, include

import djangolti.views
from peer_review.views.core import *
from peer_review.views.special import DebugLtiParamsView, SafariLaunchPopup
from peer_review.decorators import permission_denied


def not_found(request):
    raise Http404


urlpatterns = [
    url(r'^who_am_i/', who_am_i),  # TODO remove this
    url(r'^course/(?P<course_id>[0-9]+)/', include([

        url(r'^favicon.ico$', not_found),   # TODO ...just add a favicon already

        url(r'^health/', include('health_check.urls')),

        url(r'^$', CourseIndexView.as_view()),
        url(r'^launch$', djangolti.views.LaunchView.as_view(), name='launch'),
        url(r'^dashboard/instructor$', InstructorDashboardView.as_view()),
        url(r'^dashboard/student$', StudentDashboardView.as_view()),
        url(r'^status/rubric/(?P<rubric_id>[0-9]+)/all$', AssignmentStatus.as_view()),
        url(r'^rubric/assignment/(?P<assignment_id>[0-9]+)$', RubricCreationFormView.as_view()),
        url(r'^submissions/(?P<submission_id>[0-9]+)/download$', SubmissionDownloadView.as_view()),
        url(r'^review/submission/(?P<submission_id>[0-9]+)$', PeerReviewView.as_view()),
        url(r'^review/submission/(?P<submission_id>[0-9]+)/completed$', SingleReviewDetailView.as_view()),
        url(r'^review/students$', AllStudentsReviews.as_view()),
        url(r'^review/student/(?P<student_id>[0-9]+)$', OverviewForAStudent.as_view()),
        url(r'^review/student/(?P<student_id>[0-9]+)/download$', OverviewDownload.as_view()),
        url(r'^review/student/(?P<student_id>[0-9]+)/rubric/(?P<rubric_id>[0-9]+)$', ReviewsForAStudentView.as_view()),
        url(r'^review/student/(?P<student_id>[0-9]+)/rubric/(?P<rubric_id>[0-9]+)/download$',
            ReviewsDownload.as_view()),
        url(r'^safari$', SafariLaunchPopup.as_view()),
    ]))
]

handler403 = permission_denied

if settings.DEBUG:
    from django.contrib.auth.views import login as auth_login
    debug_patterns = [
        url(r'^accounts/login/$', auth_login, name='login'),
        url(r'^debug/lti$', DebugLtiParamsView.as_view())
    ]
    urlpatterns = debug_patterns + urlpatterns
