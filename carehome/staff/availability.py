from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from .models import Week_2
from client.models import DateInfo
from staff.models import WeekDateRange
from .forms import WeekForm_2

class SubmitAvailabilityView(FormView):
    template_name = 'staff/availability.html'
    form_class = WeekForm_2
    success_url = reverse_lazy('success_availability')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        today = datetime.today().date()
        current_week = WeekDateRange.objects.filter(start_date__lte=today, end_date__gte=today).first()
        weeks = WeekDateRange.objects.filter(year=current_week.year, week_number__gte=current_week.week_number)[:4]

        selected_week_id = request.GET.get('week_id')
        if selected_week_id:
            try:
                selected_week = WeekDateRange.objects.get(id=selected_week_id)
            except WeekDateRange.DoesNotExist:
                selected_week = current_week
        else:
            selected_week = current_week

        dates = []
        current_date = selected_week.start_date
        while current_date <= selected_week.end_date:
            dates.append({
                'date': current_date,
                'weekday': current_date.strftime('%A')
            })
            current_date += timedelta(days=1)

        form = self.form_class()

        context = {
            'form': form,
            'weeks': weeks,
            'selected_week': selected_week,
            'dates': dates,
            'staff_name': f"{request.user.first_name} {request.user.last_name}",
            'selected_week_id': selected_week.id,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_week_id = request.POST.get('week_id')
        try:
            selected_week = WeekDateRange.objects.get(id=selected_week_id)
        except WeekDateRange.DoesNotExist:
            messages.error(request, "Selected week does not exist.")
            return redirect('some_error_page')

        staff_name = f"{request.user.first_name} {request.user.last_name}"
        dates = DateInfo.objects.filter(week=selected_week)

        for date_info in dates:
            staff_availability_1_key = f"staff_availability_1_{date_info.date}"
            staff_availability_2_key = f"staff_availability_2_{date_info.date}"

            staff_availability_1 = request.POST.get(staff_availability_1_key, False) == 'on'
            staff_availability_2 = request.POST.get(staff_availability_2_key, False) == 'on'

            # Check if there is an existing entry for this date
            week_entry, created = Week_2.objects.get_or_create(
                date=date_info.date,
                week_name=selected_week.week_name,
                staff_name=staff_name, 
                defaults={
                    'week_day': date_info.weekday,
                    'staff_availability_1': staff_availability_1,
                    'staff_availability_2': staff_availability_2,
                }
            )

            if not created:
                # Update the existing entry
                week_entry.week_day = date_info.weekday
                week_entry.staff_name = staff_name
                week_entry.staff_availability_1 = staff_availability_1
                week_entry.staff_availability_2 = staff_availability_2
                week_entry.save()

        return redirect(self.success_url)
