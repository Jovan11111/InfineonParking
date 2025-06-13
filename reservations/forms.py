from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Company

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="email")
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=True, help_text="Izaberi firmu")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'company','password1', 'password2']