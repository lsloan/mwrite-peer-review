from django.http import Http404
from django.conf import settings
from django.conf.urls import url, include

import djangolti.views
import peer_review.api.endpoints as api
from peer_review.views.core import *
from peer_review.views.special import DebugLtiParamsView, SafariLaunchPopup, permission_denied


def not_found(request):
    raise Http404


urlpatterns = [

    url(r'^launch$', djangolti.views.LaunchView.as_view(), name='launch'),
    url(r'^user/self$', api.logged_in_user_details),

    url(r'^course/(?P<course_id>[0-9]+)/', include([

        url(r'^students/', api.all_students),

        url(r'^rubric/peer_review_assignment/(?P<passback_assignment_id>[0-9]+)/', api.rubric_info_for_peer_review_assignment),

        url(r'^reviews/rubric/(?P<rubric_id>[0-9]+)/', api.review_status),
        url(r'^reviews/student/(?P<student_id>[0-9]+)/', include([
            url(r'^assigned', api.assigned_work),
            url(r'^completed', api.completed_work),
            url(r'^given/(?P<rubric_id>[0-9]+)', api.reviews_given),
            url(r'^received/(?P<rubric_id>[0-9]+)', api.reviews_received),
            url(r'^evaluation/(?P<peer_review_id>[0-9]+)', api.submit_peer_review_evaluation)
        ])),

        url(r'^peer_review/all', api.all_peer_review_assignment_details),

        ### old URLs below this point

        url(r'^favicon.ico$', not_found),   # TODO ...just add a favicon already

        url(r'^health/', include('health_check.urls')),

        url(r'^$', CourseIndexView.as_view()),
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
