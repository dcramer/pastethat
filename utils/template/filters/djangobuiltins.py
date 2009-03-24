from jinja.contrib.djangosupport import register, convert_django_filter

from django.contrib.humanize.templatetags.humanize import intcomma, intword
from django.template.defaultfilters import filesizeformat, date

register.filter(convert_django_filter(filesizeformat), 'filesizeformat')
register.filter(convert_django_filter(date), 'date')
register.filter(convert_django_filter(intcomma), 'intcomma')
register.filter(convert_django_filter(intword), 'intword')

from pastethat.utils import url
register.object(url)