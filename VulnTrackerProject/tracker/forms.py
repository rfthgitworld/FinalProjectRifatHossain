
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    """Custom User Creation Form to handle registration."""
    class Meta:
        model = User
        fields = ('username', 'email') # Add email for a richer profile