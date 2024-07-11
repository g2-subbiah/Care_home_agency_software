# forms.py

from django import forms
from .models import TimeSheet, Week_2
from Agency.models import CustomUser
from django.utils import timezone
from .models import TimeSheet
from Agency.forms import ClientLoginForm 
from django.contrib.auth import get_user_model


CustomUser = get_user_model()

class TimeSheetForm(forms.ModelForm):
    class Meta:
        model = TimeSheet
        fields = [
            'care_home_id', 'date_of_work', 'shift_started_time',
            'break_started_time', 'break_finished_time', 'shift_finished_time',
            'client_rep_name', 'client_rep_position',
            'staff_signature_image', 'client_rep_signature_image'
        ]

        widgets = {
            'shift_started_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'shift_finished_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'break_started_time': forms.TimeInput(attrs={'type': 'time'}),
            'break_finished_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['care_home_id'].queryset = CustomUser.objects.filter(groups__name='client')
        self.fields['date_of_work'].initial = timezone.now().date()



class WeekForm_2(forms.ModelForm):
    class Meta:
        model = Week_2
        fields = ['date', 'week_name', 'week_day', 'staff_name', 'staff_availability_1', 'staff_availability_2']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'week_name': forms.TextInput(attrs={'class': 'form-control'}),
            'week_day': forms.TextInput(attrs={'class': 'form-control'}),
            'staff_name': forms.TextInput(attrs={'class': 'form-control'}),
         }

    staff_availability_1 = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    staff_availability_2 = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user from kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.fields['staff_name'].initial = f"{user.first_name} {user.last_name}"
        for field in self.fields.values():
            field.required = True