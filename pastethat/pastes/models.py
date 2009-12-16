from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.conf import settings

import datetime
import random
import os.path
import time
import cgi

from jinja2 import Markup

from pygments import highlight, lexers, formatters
from pygments.util import ClassNotFound

PASTE_TYPE_TEXT = 0
PASTE_TYPE_FILE = 1
PASTE_TYPE_LINK = 2
PASTE_TYPE_IMAGE = 3

PASTE_TYPE = (
    (PASTE_TYPE_TEXT, 'Text'),
    (PASTE_TYPE_FILE, 'File'),
    (PASTE_TYPE_LINK, 'Link'),
    (PASTE_TYPE_IMAGE, 'Image'),
)
PASTE_STATUS = (
    (-1, 'Hidden'),
    (0, 'Private'),
    (1, 'Public')
)
RESERVED_SLUGS = ('recent', 'admin', 'browse', 'users', 'accounts', 'search', 'tags', 'view', 'tag', 'new')

"""
from pastethat.pastes.models import Syntax
from pygments.lexers._mapping import LEXERS

for name, item in LEXERS.iteritems():
    Syntax.objects.create(name=item[1], lexer=name)
"""

class Syntax(models.Model):
    name    = models.CharField(max_length=32)
    slug    = models.SlugField(blank=True, unique=True)
    lexer   = models.CharField(max_length=32)
    order   = models.IntegerField(default=10)
    parent  = models.ForeignKey('self', blank=True, null=True)
    children= models.SmallIntegerField(default=0)

    class Meta:
        ordering = ('parent__id', 'order', 'name')

    def __unicode__(self):
        return self.name
        
    def save(self):
        self.children = Syntax.objects.filter(parent=self).count()
        if self.parent:
            self.parent.save()
        super(Syntax, self).save()

class Group(models.Model):
    subdomain= models.CharField(max_length=16, unique=True)
    name    = models.CharField(max_length=64)
    url     = models.URLField(blank=True, null=True, verify_exists=False)
    default_syntax = models.ForeignKey(Syntax, blank=True, null=True)

    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return "http://%s.%s/" % (self.subdomain, settings.BASE_DOMAIN)

class Paste(models.Model):
    id      = models.CharField(max_length=16, primary_key=True)
    type    = models.IntegerField(choices=PASTE_TYPE)
    group   = models.ForeignKey(Group)
    parent  = models.ForeignKey('self', blank=True, null=True)
    status  = models.IntegerField(choices=PASTE_STATUS, default=0)
    text    = models.TextField(blank=True, null=True)
    # TODO: add size column, remove need for local files (s3)
    file    = models.FileField(upload_to="files/%Y/%m/%d", blank=True, null=True)
    syntax  = models.ForeignKey(Syntax, null=True, blank=True)

    title   = models.CharField(max_length=64, blank=True, null=True)
    ip      = models.IPAddressField()
    
    author  = models.ForeignKey(User, blank=True, null=True)
    post_date = models.DateTimeField(default=datetime.datetime.now, editable=False)

    children= models.IntegerField(default=0, editable=False)
    
    def __unicode__(self):
        return self.get_name()
    
    def can_delete(self, request):
        if request.user.is_authenticated() and not (paste.author == request.user or request.user.has_perm('pastes.delete_paste')):
            return False
        elif str(paste.id) not in request.session.getlist('pastes'):
            return False
        elif paste.post_date < datetime.datetime.now()-datetime.timedelta(days=1) and not request.user.has_perm('pastes.delete_paste'):
            return False
        return True
    
    @staticmethod
    def generate_key(self, length=5):
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(letters) for x in xrange(length))
    
    def get_parsed(self, syntax=None):
        if not syntax:
            syntax = self.syntax
        if not syntax:
            return (Markup(cgi.escape(self.text)), None)
        lexer = getattr(lexers, syntax.lexer)
        if lexer:
            formatter = formatters.HtmlFormatter(cssclass="highlight-%s" % self.id)
            return (Markup(highlight(self.text, lexer(), formatter)), formatter.get_style_defs('.highlight-%s' % self.id))
        else:
            return (Markup(cgi.escape(self.text)), None)

    def get_parsed_summary(self, length=255, syntax=None):
        if not syntax:
            syntax = self.syntax
        if not self.text:
            return (None, None)
        text = self.text[:length]
        if not syntax:
            return (Markup(cgi.escape(text)), None)
        lexer = getattr(lexers, syntax.lexer)
        if lexer:
            formatter = formatters.HtmlFormatter(cssclass="highlight-%s" % self.id)
            return (Markup(highlight(text, lexer(), formatter)), formatter.get_style_defs('.highlight-%s' % self.id))
        else:
            return (Markup(cgi.escape(text)), None)
    
    def save(self):
        super(Paste, self).save()
        if self.parent:
            self.parent.children = Paste.objects.filter(parent=self.parent).count()
            self.parent.save()
    
    def get_file_basename(self):
        return os.path.basename(self.file.path)
    
    def get_thumbnail_path(self):
        return 'thumbnails/%s/%s.jpg' % (time.strftime('%Y/%m/%d'), self.file,)
    
    def get_name(self):
        return self.title or 'Unnamed'
    
    def get_thumbnail_url(self):
        return "%s/%s.jpg" % (settings.BASE_URL, self.id)
    
    def get_absolute_url(self):
        return "%s/%s" % (settings.BASE_URL, self.id)
    
    def get_followup_url(self):
        return "%s/%s/followup" % (settings.BASE_URL, self.id)

    def get_children_url(self):
        return "%s/%s/children" % (settings.BASE_URL, self.id)
    
    def get_edit_url(self):
        return "%s/%s/edit" % (settings.BASE_URL, self.id)

    def get_download_url(self):
        return "%s/%s/get" % (settings.BASE_URL, self.id)

    def get_syntax_url(self, syntax):
        if self.syntax == syntax:
            return self.get_absolute_url()
        return "%s/%s/syntax/%s" % (settings.BASE_URL, self.id, syntax.slug)