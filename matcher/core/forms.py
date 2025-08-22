from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "department", "password1", "password2"]

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "department"]
