from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Client name')  # Change the label here

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'email', 'password1', 'password2']

class ClientLoginForm(forms.Form):
    username = forms.ModelChoiceField(queryset=CustomUser.objects.filter(groups__name='client'), empty_label="Select a client", widget=forms.Select(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))



