from django.shortcuts import render, redirect
from .models import Week, DateInfo
from .forms import WeekForm 
from staff.models import WeekDateRange
from datetime import datetime, date, timedelta
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views import View
import logging
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class SubmitRequirementView(FormView):
    template_name = 'client/clientfrontpage.html'
    form_class = WeekForm
    success_url = reverse_lazy('success_requirement')

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

        # form_df = pd.DataFrame(dates)
        # form_df['week_name'] = selected_week.week_name
        # form_df['care_home_name'] = request.user.first_name
        # form_df['selected_week_id'] = selected_week.id

        context = {
            'form': form,
            'weeks': weeks,
            'selected_week': selected_week,
            'dates': dates,
            'first_name': request.user.first_name,
            'selected_week_id': selected_week.id,
            #'form_df': form_df,
        }

        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        selected_week_id = request.POST.get('week_id')
        selected_week = WeekDateRange.objects.get(id=selected_week_id)


        dates = DateInfo.objects.filter(week=selected_week)

        for counter, date_info in enumerate(dates, 1):
            staff_required_1_key = f"staff_required_1_{date_info.date}"
            staff_required_2_key = f"staff_required_2_{date_info.date}"
            staff_required_3_key = f"staff_required_3_{date_info.date}"
            staff_required_4_key = f"staff_required_4_{date_info.date}"

            staff_required_1 = request.POST.get(staff_required_1_key)
            staff_required_2 = request.POST.get(staff_required_2_key)
            staff_required_3 = request.POST.get(staff_required_3_key)
            staff_required_4 = request.POST.get(staff_required_4_key)

            staff_required_1 = int(staff_required_1) if staff_required_1 else 0
            staff_required_2 = int(staff_required_2) if staff_required_2 else 0
            staff_required_3 = int(staff_required_3) if staff_required_3 else 0
            staff_required_4 = int(staff_required_4) if staff_required_4 else 0


            week_entry = Week(
                date=date_info.date,
                week_name=selected_week.week_name,
                week_day=date_info.weekday,
                care_home_name=request.user.first_name,
                staff_required_1=staff_required_1,
                staff_required_2=staff_required_2,
                staff_required_3=staff_required_3,
                staff_required_4=staff_required_4
            )
            week_entry.save()

        return redirect(self.success_url)

