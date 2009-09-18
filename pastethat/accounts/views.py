from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from django.utils import simplejson as json
from pastethat.utils.resolver import url
from pastethat.utils.template.shortcuts import render_to_response, render_to_string

from helpers import get_next_url

from models import LostPasswordHash
from forms import *

import datetime

def login_required(post_only=False):
    def wrapped(func):
        def inner(request, *args, **kwargs):
            # If request.POST is not empty we need to verify they
            # are logged in. If they are not we need to store the request
            # and ask them to login or register, and then send them
            # back to the page they requested originally with the
            # full request in tact.
            if not request.user.is_authenticated() and (not post_only or request.POST):
                if '_loginform' not in request.session or request.session['_loginform'].get('url') != request.path:
                    request.session['_loginform'] = {
                        'url': request.path,
                        'POST': request.POST,
                        'GET': request.GET,
                    }
                context = handle_login(request, flush=False)
                if context['logged_in']:
                    request.POST = request.session['_loginform']['POST']
                    request.GET = request.session['_loginform']['GET']
                    if '_loginform' in request.session:
                        del request.session['_loginform']
                    return func(request, *args, **kwargs)
                else:
                    return show_login(request)
            else:
                return func(request, *args, **kwargs)
        return inner
    return wrapped

def handle_login(request, flush=True):
    """Main view logic for logging in. Passing flush=True will clean the stored session data."""
    context = {
        'logged_in': True,
    }
    def success():
        if flush and '_loginform' in request.session:
            del request.session['_loginform']
        return context

    if request.user.is_authenticated():
        return success()

    if request.POST.get('action') == 'login':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(
                username=login_form.cleaned_data['login'],
                password=login_form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return success()
            else:
                login_form.errors['__all__'] = 'Invalid login or password.'
        register_form = RegisterForm()
    elif request.POST.get('action') == 'register':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user = User(
                username=register_form.cleaned_data['username'],
                email=register_form.cleaned_data['email'],
            )
            user.set_password(register_form.cleaned_data['password'])
            user.save()
            user = authenticate(
                username=register_form.cleaned_data['username'],
                password=register_form.cleaned_data['password'],
            )
            login(request, user)
            return success()
        login_form = LoginForm()
    else:
        login_form = LoginForm()
        register_form = RegisterForm()
    
    context.update({
        'logged_in': False,
        'login_form': login_form,
        'register_form': register_form,
    }) 
    return context
    
@never_cache
def show_login(request):
    # TODO: clean this logic up
    default_url = url('accounts')
    next_url = request.build_absolute_uri(get_next_url(request, default_url))
    login_url = request.build_absolute_uri(url('accounts.login'))
    register_url = request.build_absolute_uri(url('accounts.register'))
    if next_url.startswith(login_url) or next_url.startswith(register_url):
        next_url = default_url
    if request.user.is_authenticated():
        return HttpResponseRedirect(next_url)
        
    if request.path.startswith(url('accounts.register')):
        active_form = 'register'
    else:
        active_form = 'login'
    
    context = handle_login(request)
    if context['logged_in']:
        return HttpResponseRedirect(next_url)
    
    context.update({
        'active_form': active_form,
        'next_url': next_url,
        'TITLE': 'Login or Register',
    })
    return render_to_response('accounts/login.html', context, request)

@login_required()
def show_dashboard(request):
    # XXX: Lazy hack for now
    from pastethat.pastes.templatetags.pastes import *
    paste_list = get_recent_pastes(request.user)
    css, parsed = get_parser_summary_cache(paste_list)

    TITLE = 'Your Account'

    context = locals()
    return render_to_response('accounts/index.html', context, request)

@login_required()
def show_pastes(request):
    context = {
        'paste_list': request.user.paste_set.all().order_by('-post_date'),
        'TITLE': 'Your Pastes',
    }
    return render_to_response('accounts/pastes.html', context, request)

@login_required()
def show_settings(request):
    if request.POST:
        if request.POST.get('save'):
            form = SettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                try:
                    User.objects.exclude(pk=request.user.id).get(email=form.cleaned_data['email'])
                except User.DoesNotExist:
                    pass
                else:
                    form.errors['email'] = 'That email address is already registered with another account.'
            if form.is_valid():
                form.commit()
                return HttpResponseRedirect(url('accounts.settings') + '?success=1')
    else:
        form = SettingsForm(instance=request.user)

    context = {
        'form': form,
        'TITLE': 'Settings',
    }
    return render_to_response('accounts/settings.html', context, request)

@login_required()
def show_change_password(request):
    if request.POST:
        if request.POST.get('save'):
            form = ChangePasswordForm(request.user, request.POST)
            if form.is_valid():
                request.user.set_password(form.cleaned_data['password'])
                request.user.save()
                return HttpResponseRedirect(url('accounts.password') + '?success=1')
        elif request.POST.get('cancel'):
            return HttpResponseRedirect(url('accounts'))
    else:
        form = ChangePasswordForm(request.user)

    context = {
        'form': form,
        'TITLE': 'Change Password',
    }
    return render_to_response('accounts/change_password.html', context, request)

def recover_password_confirm(request, user_id, hash):
    context = {
        'TITLE': 'Recover Password',
    }

    try:
        password_hash = LostPasswordHash.objects.get(user=user_id, hash=hash)
        if not password_hash.is_valid:
            password_hash.delete()
            raise LostPasswordHash.DoesNotExist
        user = password_hash.user
    except LostPasswordHash.DoesNotExist:
        tpl = 'accounts/recover/failure.html'
    else:
        tpl = 'accounts/recover/confirm.html'
        if request.POST:
            form = ChangePasswordRecoverForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.save()
                # Ugly way of doing this, but Django requires the backend be set
                user = authenticate(
                    username=user.username,
                    password=form.cleaned_data['password'],
                )
                login(request, user)
                password_hash.delete()
                return HttpResponseRedirect(url('accounts'))
        else:
            form = ChangePasswordRecoverForm()
        context['form'] = form

    return render_to_response(tpl, context, request)

def recover_password(request):
    if request.POST:
        form = RecoverPasswordForm(request.POST)
        if form.is_valid():
            password_hash, created = LostPasswordHash.objects.get_or_create(
                user=form.cleaned_data['email']
            )
            if not password_hash.is_valid:
                created = True
                password_hash.date_added = datetime.datetime.now()
                password_hash.set_hash()
            if not created:
                form.errors['__all__'] = 'A password reset was already attempted for this account within the last 24 hours.'
            
        if form.is_valid():
            context = context_processors.default(request)
            context.update({
                'user': password_hash.user,
                'url': request.build_absolute_uri(password_hash.get_absolute_url()),
            })
            data = render_to_string('accounts/recover/emails/recover.txt', context)
            send_mail('[Nibbits] Password Recovery', data, settings.EMAIL_FROM_ADDRESS, [password_hash.user.email], fail_silently=True)
            form = RecoverPasswordForm()
    else:
        form = RecoverPasswordForm()
    
    breadcrumbs = (
        ('Account', url('accounts')),
        ('Recover Password', url('accounts.password.recover')),
    )

    context = {
        'form': form,
        'TITLE': 'Recover Password',
        'BREADCRUMBS': breadcrumbs,
    }
    return render_to_response('accounts/recover/index.html', context, request)

@never_cache
def js_user(request):
    context = {
        'is_authenticated': request.user.is_authenticated(),
        'messages': [],
    }
    
    if context['is_authenticated']:
        context.update(request.user.get_data())

    return HttpResponse(json.dumps(context))