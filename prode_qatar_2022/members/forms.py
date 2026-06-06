from django.conf import settings
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    def clean_username(self):
        username = self.cleaned_data.get("username", "")
        if username.lower() in settings.RESERVED_USERNAMES:
            raise ValidationError("Este nombre de usuario no está permitido.")
        return super().clean_username()
