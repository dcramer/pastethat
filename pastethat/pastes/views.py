from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.conf import settings

from pastethat.utils.template.shortcuts import render_to_response

from pygments import highlight, lexers, formatters
from pygments.util import ClassNotFound

from pastethat.utils import url

from models import PASTE_TYPE_TEXT, PASTE_TYPE_FILE, PASTE_TYPE_LINK, PASTE_TYPE_IMAGE, Paste, Syntax
from forms import PasteFileForm, PasteLinkForm, PasteTextForm

import os
import sys
import re
import PIL.Image
try: import cStringIO as StringIO
except ImportError: import StringIO
#import stat

IMAGE_TYPES = re.compile('(:?jpg|png|gif|jpeg)$', re.I)

def index(request):
    return new_paste(request)

def recent_pastes(request):
    paste_list = Paste.objects.filter(status=1, group=request.group)\
            .select_related('author').order_by('-post_date')
    
    context = {
        'PAGE': 'recent',
        'paste_list': paste_list,
    }
    return render_to_response('pastes/recent.html', context, request)

def view_paste(request, id, syntax=None):
    try:
        paste = Paste.objects.get(pk=id)
    except Paste.DoesNotExist:
        raise Http404("Paste not found")
    
    if paste.status < 0 and not (request.user.is_superuser or request.user == paste.author):
        raise Http404("Paste not found")
    
    context = {
        'PAGE': 'view',
        'paste': paste,
    }

    if paste.type == PASTE_TYPE_TEXT:
        if syntax:
            try:
                syntax = Syntax.objects.get(slug=syntax)
            except Syntax.DoesNotExist:
                return HttpResponseRedirect(paste.get_absolute_url())
        else:
            syntax = paste.syntax
        context['parsed'], context['css'] = paste.get_parsed(syntax)
        context['syntax'] = syntax
        context['syntax_list'] = Syntax.objects.all().order_by('name')

    return render_to_response('pastes/view.html', context, request)

def delete_paste(request, id):
    try:
        paste = Paste.objects.get(pk=id)
        if not paste.can_delete(request):
            raise Paste.DoesNotExist
    except Paste.DoesNotExist:
        return HttpResponseRedirect(url('pastes.new'))

    paste.status = -1
    paste.save()
    
    return HttpResponseRedirect(paste.get_absolute_url())
    
def new_paste(request, id=None):
    text_form = file_form = link_form = None

    if id:
        try:
            paste = Paste.objects.get(pk=id)
        except Paste.DoesNotExist:
            return HttpResponseRedirect(url('pastes.new'))
        parent = paste.parent or paste
    else:
        parent = paste = None

    if request.method == 'POST':
        paste_type = int(request.POST.get('type', 0))
        if paste_type == PASTE_TYPE_TEXT:
            text_form = PasteTextForm(request.POST, prefix="text")
            text_form.is_active = True
            form = text_form
        elif paste_type == PASTE_TYPE_FILE:
            file_form = PasteFileForm(request.POST, request.FILES, prefix="file")
            file_form.is_active = True
            form = file_form
        elif paste_type == PASTE_TYPE_LINK:
            link_form = PasteLinkForm(request.POST, prefix="link")
            link_form.is_active = True
            form = link_form
        if form.is_valid():
            key = form.cleaned_data['slug']
            if not key:
                length = 5
                while 1:
                    key = Paste.generate_key(length)
                    try:
                        Paste.objects.get(pk=key)
                    except Paste.DoesNotExist:
                        break
                    length += 1

            new_paste = Paste(
                id=key,
                parent=parent,
                type=paste_type,
                status=form.cleaned_data.get('public') and 1 or 0,
                title=form.cleaned_data.get('title', None),
                ip=request.META['REMOTE_ADDR'],
                author=request.user.is_authenticated() and request.user or None,
                group=request.group,
            )
            if form is text_form:
                new_paste.text = text_form.cleaned_data['text']
                if not text_form.cleaned_data['syntax']:
                    # Automatic detection
                    try:
                        lexer = lexers.guess_lexer(new_paste.text)
                        syntax = Syntax.objects.filter(lexer=lexer.__class__.__name__)[0:1].get()
                    except (Syntax.DoesNotExist, ClassNotFound), exc:
                        syntax = Syntax.objects.get(name="Plaintext")
                    new_paste.syntax = syntax
                else:
                    new_paste.syntax = text_form.cleaned_data['syntax']
            elif form is link_form:
                new_paste.text = link_form.cleaned_data['text']
            elif form is file_form:
                content = form.cleaned_data['file'].read()
                filename = form.cleaned_data['file'].name
                if not new_paste.title:
                    new_paste.title = filename
                if IMAGE_TYPES.search(filename):
                    new_paste.type = PASTE_TYPE_IMAGE
                else:
                    syntax = None
                    if len(content) < 1024*25: # 10 kb
                        try:
                            lexer = lexers.guess_lexer_for_filename(filename, content)
                            syntax = Syntax.objects.filter(lexer=lexer.__class__.__name__)[0:1].get()
                        except (Syntax.DoesNotExist, ClassNotFound):
                            pass
                    if syntax:
                        new_paste.syntax = syntax
                        new_paste.type = PASTE_TYPE_TEXT
                        new_paste.text = content
                new_paste.file.save(filename, form.cleaned_data['file'])
                request.session.setdefault('pastes', []).append(str(new_paste.id))
                request.session.save()
            new_paste.save()
            return HttpResponseRedirect(new_paste.get_absolute_url())

    if parent:
        syntax = parent.syntax_id
    elif paste and paste.syntax:
        syntax = paste.syntax_id
    else:
        syntax = request.group.default_syntax_id

    initial = {
        'parent': parent,
        'public': False,
        'paste': paste,
        'syntax': syntax,
    }

    if text_form is None:
        text_initial = initial
        if paste and paste.type == PASTE_TYPE_TEXT:
            text_initial['text'] = paste.text
        text_form = PasteTextForm(initial=text_initial, prefix="text")
    if file_form is None:
        file_form = PasteFileForm(initial=initial, prefix="file")
    if link_form is None:
        link_form = PasteLinkForm(initial=initial, prefix="link")

    if request.method == 'GET':
        text_form.is_active = True
    
    if paste:
        PAGE = 'followup'
        title = 'Post Follow-up'
        form_url = paste.get_followup_url()
    else:
        PAGE = 'new'
        title = 'New Paste'
        form_url = url('pastes.new')
    
    context = {
        'PAGE': PAGE,
        'title': title,
        'paste': paste,
        'form_url': form_url,
        'text_form': text_form,
        'file_form': file_form,
        'link_form': link_form,
    }
    
    return render_to_response('pastes/new.html', context, request)

def download_paste(request, id):
    try:
        paste = Paste.objects.get(pk=id)
    except Paste.DoesNotExist:
        raise Http404("Paste not found")
    
    if not paste.file and paste.type == PASTE_TYPE_TEXT:
        response = HttpResponse(paste.text)
        response['Content-Type'] = 'text/plain'
        return response

    return HttpResponseRedirect(paste.file.url)

    f = open(paste.file.path, 'rb')
    response = HttpResponse(f)
    response['Content-Disposition'] = 'attachment; filename="%s"' % (paste.get_file_basename())
    return response

def edit_paste(request, id):
    pass

def view_children(request, id):
    try:
        paste = Paste.objects.get(pk=id)
    except Paste.DoesNotExist:
        raise Http404("Paste not found")
    
    child_list = paste.paste_set.all().order_by('-post_date')
    
    context = {
        'PAGE': 'children',
        'paste': paste,
        'child_list': child_list,
    }
    return render_to_response('pastes/children.html', context, request)

def post_followup(request, id):
    return new_paste(request, id)

def view_thumbnail(request, id):
    try:
        paste = Paste.objects.get(pk=id)
    except Paste.DoesNotExist:
        raise Http404("Paste not found")

    thumb_path = paste.get_thumbnail_path()
    outfile = "%s/%s" % (settings.MEDIA_ROOT, thumb_path)
    try:
        f = file(outfile)
    except IOError:
        try:
            os.makedirs(os.path.dirname(outfile), 0755)
        except OSError:
            pass
        im = PIL.Image.open(paste.file.path)
        im.thumbnail((150, 100))
        im.save(outfile, "JPEG")
        f = file(outfile)

    try:
        output = ''.join(line for line in f)
    finally:
        f.close()
    response = HttpResponse(output)
    response['Content-Type'] = 'image/jpeg'
    return response