from django.conf import settings
from django.conf.urls import url, include

import djangolti.views
import peer_review.api.endpoints as api
from peer_review.api.debug import DebugLtiParamsView
from peer_review.api.special import permission_denied, not_found, server_error, SafariLaunchPopup


urlpatterns = [
    url(r'^safari$', SafariLaunchPopup.as_view(), name='safari_launch_popup'),

    url(r'^launch$', djangolti.views.LaunchView.as_view(), name='launch'),
    url(r'^user/self$', api.logged_in_user_details),

    url(r'^course/(?P<course_id>[0-9]+)/', include([
        url(r'^students/', include([
            url(r'^$', api.all_students),  # TODO change URI to /all/ ?
            url(r'^(?P<student_id>[0-9]+)/', include([
                url(r'^$', api.student_info),
                url(r'^data/', include([
                    url(r'^$', api.csv_for_student_and_rubric),
                    url(r'^rubric/(?P<rubric_id>[0-9]+)', api.csv_for_student_and_rubric)
                ]))
            ]))
        ])),

        url(r'^rubric/', include([   # TODO change URI to /rubrics/ ?
            url(r'^$', api.create_or_update_rubric),
            url(r'^all/', include([
                url(r'^$', api.all_rubrics_for_course),
                url(r'^for-student/(?P<student_id>[0-9]+)/', api.all_rubric_statuses_for_student)
            ])),
            url(r'(?P<rubric_id>[0-9]+)/for-student/(?P<student_id>[0-9]+)/',
                api.rubric_status_for_student
            )
        ])),

        url(
            r'^rubric/peer_review_assignment/(?P<passback_assignment_id>[0-9]+)/',
            api.rubric_info_for_peer_review_assignment
        ),

        url(r'^reviews/', include([
            url(r'^(?P<review_id>[0-9]+)/', include([
                url(r'^$', api.dispatch_peer_review_request),
                url(r'^submission/', api.submission_for_review),
                url(r'^rubric/', api.rubric_for_review),
            ])),
            url(r'^rubric/(?P<rubric_id>[0-9]+)/', include([
                url(r'^$', api.review_status),
                url(r'unassigned/', api.non_reviewers_for_rubric),
                url(r'assign/', api.add_students_to_distribution)
            ])),
            url(r'^student/(?P<student_id>[0-9]+)/', include([
                url(r'^assigned', api.assigned_work),
                url(r'^completed', api.completed_work),
                url(r'^given/(?P<rubric_id>[0-9]+)', api.reviews_given),
                url(r'^received/(?P<rubric_id>[0-9]+)', api.reviews_received),
                url(r'^evaluation/(?P<peer_review_id>[0-9]+)', api.submit_peer_review_evaluation)
            ]))
        ])),

        url(r'^peer_review/all', api.all_peer_review_assignment_details),
    ]))
]

handler403 = permission_denied
handler404 = not_found
handler500 = server_error

if settings.DEBUG:
    from django.contrib.auth.views import login as auth_login
    debug_patterns = [
        url(r'^accounts/login/$', auth_login, name='login'),
        url(r'^debug/lti$', DebugLtiParamsView.as_view())
    ]
    urlpatterns = debug_patterns + urlpatterns
