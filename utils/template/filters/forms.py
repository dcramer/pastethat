from django.forms.forms import BoundField
from django.template.defaultfilters import escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from jinja.contrib.djangosupport import register

def render_form(include_fields=None, exclude_fields=None, ordering=None):
    def wrapped(env, context, form):
        normal_row = u'<div id="%(row_id)s" class="formRow %(class_names)s">%(label)s %(field)s%(help_text_wrapped)s%(errors)s</div>'        
        inline_row = u'<div class="formRow %(class_names)s"><label>%(field)s %(help_text)s</label>%(errors)s</div>'
        error_row = u'<div class="formRow fInputErrorRow">%s</div>'
        class_prefix = 'f'
        row_ender = '</div>'

        top_errors = form.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []
        if include_fields:
            if exclude_fields:
                _fields = ((name, field) for name, field in form.fields.iteritems() if name in include_fields and name not in exclude_fields)
            else:
                _fields = ((name, field) for name, field in form.fields.iteritems() if name in include_fields)
        elif exclude_fields:
            _fields = ((name, field) for name, field in form.fields.iteritems() if name not in exclude_fields)
        else:
            _fields = form.fields.iteritems()
        if ordering:
            _fields = tuple(_fields)
            _fields = (f for f in ordering if f in _fields)
        for name, field in _fields:
            bf = BoundField(form, field, name)
            bf_errors = form.error_class([escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                if bf.label:
                    label_text = escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in
                    # punctuation.
                    if form.label_suffix:
                        if label_text[-1] not in ':?.!':
                            label_text += form.label_suffix
                else:
                    label_text = ''

                params = {
                    'errors': force_unicode(bf_errors),
                    'row_id': 'id_%s_wrap' % (name),
                    'label': force_unicode(bf.label_tag(label_text) or ''),
                    'field': bf,
                    'help_text': force_unicode(field.help_text or ''),
                    'help_text_wrapped': field.help_text and '<small class="helptext">%s</small>' % field.help_text or '',
                }

                widget = unicode(bf.field.widget.__class__.__name__)
                class_names = [class_prefix + widget + 'Row']
                if field.required:
                    class_names.append(class_prefix + 'Required')
                if bf.errors:
                    class_names.append(class_prefix + 'Errors')
                params['class_names'] = ' '.join(class_names)

                # XXX: Bad Hack
                if widget in ('CheckboxInput', 'RadioInput') and params['help_text']:
                    output.append(inline_row % params)
                else:
                    output.append(normal_row % params)
        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))
        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))
    return wrapped
register.filter(render_form, 'render_form')