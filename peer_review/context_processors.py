from django.conf import settings

# TODO once VueJS port is done none of this will be needed


def google_analytics(request):
    return {'google_analytics_tracking_id': settings.GOOGLE_ANALYTICS_TRACKING_ID}


def frontend_landing_url(request):
    return {'frontend_landing_url': settings.FRONTEND_LANDING_URL}
