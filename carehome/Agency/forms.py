from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from staff.models import WeekDateRange
from .models import StaffPreference



class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Client name') 

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'email', 'password1', 'password2']

class ClientLoginForm(forms.Form):
    username = forms.ModelChoiceField(queryset=CustomUser.objects.filter(groups__name='client'), empty_label="Select a client", widget=forms.Select(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class StaffPreferenceForm(forms.ModelForm):
    class Meta:
        model = StaffPreference
        fields = ['care_home_name', 'date', 'week_name', 'staff_required_field', 'staff_name', 'staff_required_sum']
        widgets = {
            'care_home_name': forms.HiddenInput(),
            'date': forms.HiddenInput(),
            'week_name': forms.HiddenInput(),
            'staff_required_field': forms.HiddenInput(),
            'staff_name': forms.HiddenInput(),
            'staff_required_sum': forms.HiddenInput(),
        }