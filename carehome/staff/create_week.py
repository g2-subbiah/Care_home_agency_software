from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from datetime import date, datetime
import re
from .management.commands.populate_weeks import generate_weeks_table  # Import the function from your utils module

class CreateWeeksTableView(View):
    template_name = 'agency/create_weeks.html'

    def get(self, request):
        current_year = date.today().year
        
        # Generate a list of year ranges for the next 10 years
        year_ranges = []
        for i in range(10):
            start_year = current_year + i
            end_year = start_year + 1
            year_ranges.append(f"{start_year}-{end_year}")
        
        context = {
            'year_ranges': year_ranges,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        year_range = request.POST.get('year_range')
        match = re.match(r'(\d{4})-(\d{4})', year_range)
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            if end_year == start_year + 1:  # Ensure that the year range is exactly one year apart
                try:
                    # Generate weeks for the specified year range
                    weeks_table = generate_weeks_table(start_year, end_year)
                    
                    # Assuming you are saving weeks_table to a model or using it for some purpose
                    
                    messages.success(request, f'Successfully created weeks for {start_year}-{end_year}')
                    
                    # Redirect to the 'create-weeks' page (modify as per your URL config)
                    return redirect('create-weeks')
                except Exception as e:
                    messages.error(request, f'Failed to create weeks: {str(e)}')
            else:
                messages.error(request, 'The year range must be exactly one year apart (e.g., "2024-2025").')
        else:
            messages.error(request, 'Invalid year range format. Please use "YYYY-YYYY" format.')

        # Re-generate year ranges list for the dropdown on POST request
        current_year = date.today().year
        year_ranges = []
        for i in range(10):
            start_year = current_year + i
            end_year = start_year + 1
            year_ranges.append(f"{start_year}-{end_year}")
        
        context = {
            'year_ranges': year_ranges,
            'year_range': year_range,
        }
        return render(request, self.template_name, context)
