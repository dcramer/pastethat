from django.conf import settings

def get_next_url(request, default=None, clear=True):
    """
    Grabs the commonly used next URL parameter by first checking the request,
    and then moving on to the session. If it fails, or the URL is not valid, it
    returns the BASE_URL setting.
    """
    next_url = request.REQUEST.get('next')
    if not next_url:
        next_url = request.session.get('next')
        if next_url and clear:
            del request.session['next_url']

    if not next_url:
        next_url = request.META.get('HTTP_REFERER')

    if not next_url or not (next_url.startswith('/') or next_url.startswith(settings.BASE_URL)):
        next_url = settings.BASE_URL

    if not next_url and default:
        next_url = default

    return next_url