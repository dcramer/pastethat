from django.utils.safestring import mark_safe
from pastethat.utils.paginator.paginator import EndlessPaginator
from pastethat.utils.template.shortcuts import render_to_string
from jinja2 import Markup
from coffin import template
register = template.Library()

def paginate(request, queryset_or_list, limit=25, paginator_class=EndlessPaginator):
    paginator = paginator_class(queryset_or_list, limit)
    
    query_dict = request.GET.copy()
    if 'p' in query_dict:
        del query_dict['p']

    context = {
        'query_string': query_dict.urlencode(),
        'paginator': paginator.get_context(request.GET.get('p', 1)),
    }
    paging = mark_safe(Markup(render_to_string('bone/paging.html', context)))
    return dict(objects=context['paginator'].get('objects', []), paging=paging)
register.object(paginate)
