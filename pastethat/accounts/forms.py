from django import forms
from django.contrib.auth.models import User

import re

__all__ = ('LoginForm', 'RegisterForm', 'ChangePasswordForm', 'RecoverPasswordForm', 'ChangePasswordRecoverForm', 'SettingsForm', 'AvatarForm')

class RecoverPasswordForm(forms.Form):
    email       = forms.EmailField()
    
    def clean_email(self):
        value = self.cleaned_data.get('email')
        if value:
            try:
                return User.objects.get(email=value)
            except User.DoesNotExist:
                raise forms.ValidationError("Your email address was invalid.")
        return None

class LoginForm(forms.Form):
    login       = forms.CharField(label='Email:', help_text="You may use your username or email to login.")
    password    = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    username    = forms.CharField(min_length=3, max_length=32)
    email       = forms.EmailField()
    password    = forms.CharField(widget=forms.PasswordInput())
    confirm_password    = forms.CharField(widget=forms.PasswordInput())
    
    def clean_email(self):
        value = self.cleaned_data.get('email', '')
        if value:
            try:
                User.objects.get(email__iexact=register_form.cleaned_data['email'])
            except User.DoesNotExist:
                pass
            else:
                raise forms.ValidationError('That email address is already registered.')
        return value
    
    def clean_username(self):
        value = self.cleaned_data.get('username', '')
        if re.search('[^a-zA-Z0-9_-]', value):
            raise forms.ValidationError('Your username may only contain a-z, A-Z, 0-9, - and _ characters.')
        try:
            User.objects.get(username__iexact=value)
        except User.DoesNotExist:
            pass
        else:
            raise forms.ValidationError('That username is already taken.')
        return value
    
    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('password', True) != cleaned_data.get('confirm_password', True):
            raise forms.ValidationError('Your passwords do not match.')
        return cleaned_data

class SettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

class ChangePasswordRecoverForm(forms.Form):
    password            = forms.CharField(widget=forms.PasswordInput())
    confirm_password    = forms.CharField(widget=forms.PasswordInput())
    
    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('password', True) != cleaned_data.get('confirm_password', False):
            raise forms.ValidationError('Your passwords do not match.')
        return cleaned_data

class ChangePasswordForm(forms.Form):
    current_password    = forms.CharField(widget=forms.PasswordInput())
    password            = forms.CharField(widget=forms.PasswordInput())
    confirm_password    = forms.CharField(widget=forms.PasswordInput())
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('password', True) != cleaned_data.get('confirm_password', False) or \
                not self.user.check_password(cleaned_data.get('current_password', '')):
            raise forms.ValidationError('Your passwords do not match.')
        return cleaned_data

class AvatarForm(forms.Form):
    image = forms.ImageField()