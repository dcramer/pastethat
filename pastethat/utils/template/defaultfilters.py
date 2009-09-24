from django.conf import settings

from coffin import template
register = template.Library()

def urlencode(value):
    from django.template.defaultfilters import urlencode
    return urlencode(value)
register.filter(urlencode, jinja2_only=True)

def linebreaks(value):
    from django.template.defaultfilters import linebreaks
    return linebreaks(value)
register.filter(linebreaks, jinja2_only=True)

def intcomma(value):
    from django.contrib.humanize.templatetags.humanize import intcomma
    return intcomma(value)
register.filter(intcomma, jinja2_only=True)

def truncatechars(value, length=30):
    if len(value) > length:
        value = value[0:length-3] + '...'
    return value
register.filter(truncatechars, jinja2_only=True)

try:
    from cmath import math
except ImportError:
    import math

def ceil(value):
    return math.ceil(value)
register.filter(ceil)

def floor(value):
    return math.floor(value)
register.filter(floor)

def timesince(value):
    from django.template.defaultfilters import timesince
    value = (' '.join(timesince(value).split(' ')[0:2])).strip(',')
    if value == '0 minutes':
        return 'Just now'
    return value + ' ago'
register.filter(timesince)

import os, os.path
def mediaversion(value):
    """Returns the modified time (as a string) for the media"""
    try:
        fname = os.path.abspath(os.path.join(settings.MEDIA_ROOT, value))
        if not fname.startswith(settings.PROJECT_ROOT):
            raise ValueError("Media must be located within MEDIA_ROOT.")
        return unicode(int(os.stat(fname).st_mtime))
    except OSError:
        return 0
register.object(mediaversion)

def mediaurl(value, arg=None):
    return "%s%s?%s" % (settings.MEDIA_URL, value, mediaversion(value))
register.object(mediaurl)