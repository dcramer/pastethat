from django import forms
from django.conf import settings
from django.utils.encoding import force_unicode, smart_unicode
from django.utils.safestring import mark_safe
from django.template.defaultfilters import escape
from django.forms.util import flatatt

import itertools

from models import Paste, Syntax, RESERVED_SLUGS

__all__ = ('PasteTextForm', 'PasteFileForm', 'PasteLinkForm')

class GroupedModelChoiceField(forms.ModelChoiceField):
    """A ChoiceField whose choices are a model QuerySet."""
    def _get_choices(self):
        if not hasattr(self, '_choices'):
            self._choices = []
            used = []
            if self.empty_label:
                self._choices.append((u"", self.empty_label))
            def loop(objects):
                func = lambda x: x.parent
                for parent, objects in itertools.groupby(sorted(objects, key=func), key=func):
                    if parent and parent.pk not in used:
                        used.append(parent.pk)
                        self._choices.append((parent.pk, parent))
                    for obj in objects:
                        if obj.children:
                            loop(Syntax.objects.filter(parent=obj))
                        else:
                            if obj.pk in used:
                                continue
                            if parent:
                                val = mark_safe(u'&nbsp;&nbsp;&nbsp;&nbsp;%s' % escape(obj))
                            else:
                                val = obj
                            used.append(obj.pk)
                            self._choices.append((obj.pk, val))
                        
            loop(self.queryset)
        return self._choices

    choices = property(_get_choices, forms.ModelChoiceField._set_choices)

class SlugField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('min_length', 5)
        kwargs.setdefault('max_length', 16)
        kwargs.setdefault('required', False)
        kwargs.setdefault('widget', SlugInput())
        kwargs.setdefault('help_text', "You may specify the URL slug to use for your paste. Minimum 5 characters.")
        super(SlugField, self).__init__(*args, **kwargs)
        
    def clean(self, value):
        if re.search('[^a-zA-Z0-9_-]', value):
            raise forms.ValidationError('Your slug may only contain a-z, A-Z, 0-9, - and _ characters.')
        
        if value in RESERVED_SLUGS:
            raise forms.ValidationError("You may not use that slug.")
        try:
            Paste.objects.get(pk=value)
        except Paste.DoesNotExist:
            pass
        else:
            raise forms.ValidationError("That slug is already in use.")
        return value

class SlugInput(forms.widgets.TextInput):
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'%s/<input%s />' % (settings.BASE_URL, flatatt(final_attrs)))

class PasteForm(forms.Form):
    slug    = SlugField()
    public  = forms.BooleanField(required=False, help_text="Allow others to browse and search for this paste.")
    tags    = forms.CharField(required=False, help_text="Tags are seperated with spaces or commas.")

class PasteTextForm(PasteForm):
    syntax  = GroupedModelChoiceField(queryset=Syntax.objects.all().order_by('parent', 'order', 'name'), empty_label='(Automatic)', required=False)
    text    = forms.CharField(min_length=5, widget=forms.widgets.Textarea())
    title   = forms.CharField(max_length=64, required=False)
        
class PasteFileForm(PasteForm):
    file    = forms.FileField()

class PasteLinkForm(PasteForm):
    text    = forms.URLField(label='URL')