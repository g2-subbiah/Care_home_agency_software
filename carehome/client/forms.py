from django import forms
from .models import Week

class WeekForm(forms.ModelForm):
    class Meta:
        model = Week
        fields = ['date', 'week_name', 'week_day', 'care_home_name', 'staff_required_1', 'staff_required_2', 'staff_required_3', 'staff_required_4']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'week_name': forms.TextInput(attrs={'class': 'form-control'}),
            'week_day': forms.TextInput(attrs={'class': 'form-control'}),
            'care_home_name': forms.TextInput(attrs={'class': 'form-control'}),
            'staff_required_1': forms.NumberInput(attrs={'min': 0, 'max': 99, 'class': 'form-control'}),
            'staff_required_2': forms.NumberInput(attrs={'min': 0, 'max': 99, 'class': 'form-control'}),
            'staff_required_3': forms.NumberInput(attrs={'min': 0, 'max': 99, 'class': 'form-control'}),
            'staff_required_4': forms.NumberInput(attrs={'min': 0, 'max': 99, 'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True  
