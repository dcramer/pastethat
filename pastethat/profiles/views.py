from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from pastethat.utils.resolver import url
from pastethat.utils.template.shortcuts import render_to_response

def details(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseRedirect(url('pastes.new'))

    # XXX: Lazy hack for now
    from pastethat.pastes.templatetags.pastes import *
    paste_list = user.paste_set.filter(status=1).order_by('-post_date')
    css, parsed = get_parser_summary_cache(paste_list)
    TITLE = user.username
    
    context = locals()
    return render_to_response('profiles/details.html', context, request)


def pastes(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseRedirect(url('pastes.new'))

    context = {
        'paste_list': user.paste_set.filter(status=1).order_by('-post_date'),
        'user': user,
        'TITLE': 'Pastes by %s' % (user.username,),
    }
    return render_to_response('profiles/pastes.html', context, request)
