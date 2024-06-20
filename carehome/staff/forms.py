# forms.py

from django import forms
from .models import TimeSheet
from Agency.models import CustomUser
from django.utils import timezone
from .models import TimeSheet
from Agency.forms import ClientLoginForm  # Make sure to import Client

class TimeSheetForm(forms.ModelForm):
    class Meta:
        model = TimeSheet
        fields = [
            'care_home_name', 'date_of_work', 'shift_started_time',
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
        self.fields['care_home_name'].queryset = CustomUser.objects.filter(groups__name='client')
        self.fields['date_of_work'].initial = timezone.now().date()
