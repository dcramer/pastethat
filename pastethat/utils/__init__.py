from django.core.urlresolvers import reverse, NoReverseMatch
def url(view_name, *args, **kwargs):
    # Try to look up the URL twice: once given the view name, and again
    # relative to what we guess is the "main" app. If they both fail,
    # re-raise the NoReverseMatch
    match = ''
    try:
        match = reverse(view_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        project_name = settings.SETTINGS_MODULE.split('.')[0]
        try:
            match = reverse(project_name + '.' + view_name,
                          args=args, kwargs=kwargs)
        except NoReverseMatch:
            raise
    
    return match