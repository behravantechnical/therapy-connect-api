from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


# this form use in django admin panel in admin.py module
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="password", widget=forms.PasswordInput, validators=[validate_password]
    )
    password2 = forms.CharField(
        label="confirm password",
        widget=forms.PasswordInput,
        validators=[validate_password],
    )

    class Meta:
        model = get_user_model()
        fields = ("mobile_number", "first_name", "last_name")

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password1"] and cd["password2"] and cd["password1"] != cd["password2"]:
            raise ValidationError("passwords don't match")
        return cd["password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# this form use in django admin panel in admin.py module
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        help_text='you can change password using <a href="../password/">this form</a>.'
    )

    class Meta:
        model = get_user_model()
        fields = ("mobile_number", "first_name", "last_name", "password", "last_login")
