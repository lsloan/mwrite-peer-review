from django import http
from django.template import loader, TemplateDoesNotExist
from django.utils.encoding import force_text
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_403_TEMPLATE_NAME

from peer_review.views.special import logger


# adapted from django.views.defaults.permission_denied
@requires_csrf_token
def permission_denied(request, exception, template_name=ERROR_403_TEMPLATE_NAME):
    """
    Permission denied (403) handler.

    Templates: :template:`403.html`
    Context: None

    If the template does not exist, an Http403 response containing the text
    "403 Forbidden" (as per RFC 7231) will be returned.
    """

    # M-Write Peer Review customization starts here
    if request.user.is_authenticated:
        username = 'user %s' % request.user.username

    else:
        username = 'unauthenticated user'
    lti_launch_params = request.session.get('lti_launch_params')
    if lti_launch_params:
        params_desc = lti_launch_params
    else:
        params_desc = 'nonexistent'
    logger.warning('Permission denied for %s to %s with LTI launch parameters %s'
                   % (username, request.get_full_path(), params_desc))
    # M-Write Peer Review customization ends here

    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        if template_name != ERROR_403_TEMPLATE_NAME:
            # Reraise if it's a missing custom template.
            raise
        return http.HttpResponseForbidden('<h1>403 Forbidden</h1>', content_type='text/html')
    return http.HttpResponseForbidden(
        template.render(request=request, context={'exception': force_text(exception)})
    )
