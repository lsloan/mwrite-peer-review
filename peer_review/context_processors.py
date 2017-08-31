from django.conf import settings


def google_analytics(request):
    return {'google_analytics_tracking_id': settings.GOOGLE_ANALYTICS_TRACKING_ID}
