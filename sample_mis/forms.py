# # from django import forms
# # from .models import Sample, SampleTestResult, Label
# #
# # class SampleForm(forms.ModelForm):
# #     class Meta:
# #         model = Sample
# #         fields = [
# #             'sample_type',
# #             'sample_origin',  # Corrected from 'origin'
# #             'batch_number',
# #             'testing_status'  # Corrected from 'status'
# #         ]
# #
# # class SampleTestResultForm(forms.ModelForm):
# #     class Meta:
# #         model = SampleTestResult
# #         fields = ['quality_analysis', 'compliance_status', 'expiry_date']
# #
# # class LabelForm(forms.ModelForm):
# #     class Meta:
# #         model = Label
# #         fields = ['certification_number', 'expiry_date']
# from django import forms
# from .models import Sample, SampleTestResult, Label
#
# class SampleForm(forms.ModelForm):
#     class Meta:
#         model = Sample
#         fields = ['sample_type', 'sample_origin', 'batch_number', 'testing_status']
#
# class SampleTestResultForm(forms.ModelForm):
#     class Meta:
#         model = SampleTestResult
#         fields = ['quality_analysis', 'compliance_status', 'expiry_date']
#
# class LabelForm(forms.ModelForm):
#     class Meta:
#         model = Label
#         fields = ['certification_number', 'expiry_date']
#
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth.models import User
# class LoginForm(AuthenticationForm):
#     pass
#
# class RegistrationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']
from django import forms
from .models import Sample, SampleTestResult, Label
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['sample_type', 'sample_origin', 'batch_number', 'testing_status']

class SampleTestResultForm(forms.ModelForm):
    class Meta:
        model = SampleTestResult
        fields = ['quality_analysis', 'compliance_status', 'expiry_date']

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['certification_number', 'expiry_date']

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # Add custom attributes for username field
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        # Add custom attributes for password field
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })

# class RegistrationForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']
#
#     def __init__(self, *args, **kwargs):
#         super(RegistrationForm, self).__init__(*args, **kwargs)
#         # Customize username widget
#         self.fields['username'].widget.attrs.update({
#             'class': 'form-control',
#             'placeholder': 'Choose a username'
#         })
#         # Customize email widget
#         self.fields['email'].widget.attrs.update({
#             'class': 'form-control',
#             'placeholder': 'Enter your email'
#         })
#         # Customize password1 widget
#         self.fields['password1'].widget.attrs.update({
#             'class': 'form-control',
#             'placeholder': 'Enter a password'
#         })
#         # Customize password2 widget
#         self.fields['password2'].widget.attrs.update({
#             'class': 'form-control',
#             'placeholder': 'Confirm your password'
#         })
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

from django.contrib.auth.forms import AuthenticationForm
from django import forms

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'style': 'border-radius: 50px;'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'style': 'border-radius: 50px;'
        })
    )
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from django.contrib.auth.forms import AuthenticationForm
from django import forms
#
# class CustomLoginForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#         super(CustomLoginForm, self).__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs.update({
#             'class': 'form-control',
#             'placeholder': 'Username'
#         })
#         self.fields['password'].widget.attrs.update({
#             'class': 'form-control',
#             'placeholder': 'Password'
#         })
#
# from django import forms
# from django.contrib.auth.forms import AuthenticationForm
#
# class CustomLoginForm(AuthenticationForm):
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={'placeholder': 'Enter username', 'class': 'form-control'})
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-control'})
#     )
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

