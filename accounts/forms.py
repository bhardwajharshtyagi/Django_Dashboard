from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)


class SignupForm(UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    class Meta:

        model = User

        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label,
            })

    def save(self, commit=True):

        user = super().save(
            commit=False
        )

        user.email = self.cleaned_data[
            "email"
        ]

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )

        for field in self.fields.values():

            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label,
            })


class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Email",
            }
        )
    )


class ResetPasswordForm(forms.Form):

    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter OTP",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "New Password",
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm Password",
            }
        )
    )


class ChangePasswordForm(forms.Form):

    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Current Password",
            }
        )
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "New Password",
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm Password",
            }
        )
    )


class ProfileUpdateForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "email",
        ]

        widgets = {

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }







from django import forms
from .models import SupportTicket


class SupportTicketForm(forms.ModelForm):

    class Meta:

        model = SupportTicket

        fields = [
            "subject",
            "message",
        ]

        widgets = {

            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your issue subject"
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe your problem..."
                }
            ),
        }