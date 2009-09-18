from coffin import template
register = template.Library()

def url(*args, **kwargs):
    from pastethat.utils.resolver import url
    return url(*args, **kwargs)
register.object(url)