from coffin import template
register = template.Library()

from pastethat.pastes.models import Paste

def get_random_pastes(group, limit=5):
    return Paste.objects.filter(
        group=group,
        status=1,
    ).order_by('?')[:limit]
register.object(get_random_pastes)

def get_parser_summary_cache(pastes=[]):
    css, parsed = [], {}
    for paste in pastes:
        l_parsed, l_css = paste.get_parsed_summary()
        if l_css:
            css.append(l_css)
        parsed[paste.id] = l_parsed
    return '\n'.join(css), parsed
register.object(get_parser_summary_cache)

def get_recent_pastes(user, limit=5):
    return Paste.objects.filter(
        author=user,
    ).order_by('-post_date')[:limit]
register.object(get_recent_pastes)