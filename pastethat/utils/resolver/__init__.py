from django.conf import settings
from django.core.urlresolvers import get_resolver, reverse, NoReverseMatch

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

def vary_reverse(lookup_view, kwargs):
    """
    Returns the first matching URL for the ``lookup_view``
    matching any number of ``kwargs`` in any order.
    
    vary_reverse('lookup_view', {'param1': 'value', 'param2': 'value'})
    """
    resolver = get_resolver(None)
    for result in resolver.reverse_dict.getlist(lookup_view):
        pattern, req_kwargs = result[0][0]
        if req_kwargs:
            try:
                usable_kwargs = dict([(k, kwargs[k]) for k in req_kwargs])
            except KeyError:
                continue
        else:
            usable_kwargs = {}
        return reverse(lookup_view, kwargs=usable_kwargs)
    raise ValueError('No url matching matching `%s` and kwargs: %s' % (lookup_view, kwargs))

def vary_permalink(func):
    def inner(*args, **kwargs):
        bits = func(*args, **kwargs)
        return vary_reverse(*bits)
    return inner