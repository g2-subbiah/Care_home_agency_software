
import csv
import os
import pandas as pd
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from staff.models import WeekDateRange, TimeSheet
from django.conf import settings

class WeeklyReportView(View):
    template_name = 'agency/weekly_report.html'

    def get(self, request):
        week_date_ranges = WeekDateRange.objects.all().order_by('year', 'week_number')
        context = {
            'week_date_ranges': week_date_ranges,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get('action')

        if action == 'generate_report':
            return self.generate_report(request)
        elif action == 'process_report':
            return self.process_report(request)
        
    def convert_times(self, df, start_col, end_col):
        df[start_col] = pd.to_datetime(df[start_col]).dt.strftime('%H:%M')
        df[end_col] = pd.to_datetime(df[end_col]).dt.strftime('%H:%M')
        return df

    def generate_report(self, request):
        year = request.POST.get('year')
        week_number = request.POST.get('week_number')

        week_range = WeekDateRange.objects.get(year=year, week_number=week_number)
        timesheets = TimeSheet.objects.filter(
            date_of_work__gte=week_range.start_date,
            date_of_work__lte=week_range.end_date
        )

        base_file_name = f"weekly_report_week_{week_number}.csv"
        generated_reports_dir = settings.GENERATED_REPORTS_DIR
        file_path = os.path.join(generated_reports_dir, 'Weekly_timesheet_unprocessed', base_file_name)

        # Check if the file already exists, if yes, append a number to make it unique
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(generated_reports_dir, 'Weekly_timesheet_unprocessed', f"weekly_report_week_{week_number}_{counter}.csv")
            counter += 1

        try:
            os.makedirs(os.path.join(generated_reports_dir, 'Weekly_timesheet_unprocessed'), exist_ok=True)

            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['user', 'date_of_work', 'shift_started_time', 'break_started_time', 'break_finished_time', 'shift_finished_time', 'client_rep_name', 'client_rep_position', 'care_home_name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for timesheet in timesheets:
                    # Fetch the care home name's first name
                    care_home_user = timesheet.care_home_name
                    care_home_first_name = care_home_user.first_name if care_home_user else 'N/A'
                    
                    # Debugging output
                    print(f"Timesheet ID: {timesheet.id}")
                    print(f"User: {timesheet.user.get_full_name()}")
                    print(f"Care Home Name: {care_home_first_name}")

                    writer.writerow({
                        'user': timesheet.user.get_full_name(),
                        'date_of_work': timesheet.date_of_work,
                        'shift_started_time': timesheet.shift_started_time,
                        'break_started_time': timesheet.break_started_time,
                        'break_finished_time': timesheet.break_finished_time,
                        'shift_finished_time': timesheet.shift_finished_time,
                        'client_rep_name': timesheet.client_rep_name,
                        'client_rep_position': timesheet.client_rep_position,
                        'care_home_name': care_home_first_name
                    })

            timesheets.delete()

            return HttpResponse(f'Success! CSV file generated and saved at {file_path}')
        
        except Exception as e:
            # Log the exception or handle it appropriately
            print(f"Error generating report: {e}")
            return HttpResponse(f'Error generating report: {e}', status=500)


    def process_report(self, request):
        try:
            file = request.FILES['file']
            file_path = os.path.join(settings.GENERATED_REPORTS_DIR, 'Weekly_timesheet_unprocessed', file.name)
            
            # Saving the uploaded file
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Reading the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)

            # Calculate working hours
            df['working_hours'] = (pd.to_datetime(df['shift_finished_time']) - pd.to_datetime(df['shift_started_time'])).dt.total_seconds() / 3600

            # Correctly calling the convert_times method using self
            df = self.convert_times(df, 'shift_started_time', 'shift_finished_time')

            # Adding weekday column
            df = self.add_weekday_column(df, 'date_of_work')

            # Adding rate column
            df = self.add_rate_column(df)

            df.rename(columns={'user': 'staff_name'}, inplace=True)
            df.sort_values(by=['staff_name'], inplace=True)

            df.reset_index(drop=True, inplace=True)
            df.index += 1  

            df.insert(0, 's_no', df.index)
            #columns = ['s_no', 'staff_name', 'date_of_work', 'shift_started_time', 'shift_finished_time', 'working_hours', 'weekday', 'rate', 'care_home_name']
            #df = df[columns]
            existing_columns = df.columns.tolist()

            if 'care_home_name' in existing_columns:
                existing_columns.remove('care_home_name')
                existing_columns.append('care_home_name')

            df = df[existing_columns]

            columns_to_drop = ['break_started_time', 'break_finished_time', 'client_rep_name', 'client_rep_position']
            df = df.drop(columns=columns_to_drop, errors='ignore')

            # Create the directory for processed reports if it doesn't exist
            generated_reports_dir = settings.GENERATED_REPORTS_DIR
            try:
                os.makedirs(os.path.join(generated_reports_dir, 'Weekly_processed_reports'), exist_ok=True)
            except OSError as e:
                # Handle the error (log it, raise it, etc.)
                print(f"Error creating directory: {e}")

            # Saving processed DataFrame back to CSV
            output_path = os.path.join(generated_reports_dir, 'Weekly_processed_reports', 'processed_' + file.name)
            df.to_csv(output_path, index=False)

            # Returning the processed CSV file as a response
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(output_path)}'
                return response

        except KeyError:
            return HttpResponseBadRequest('File not found in request.')
        except Exception as e:
            return HttpResponseBadRequest(f'Error processing file: {str(e)}')
        
   
    def add_weekday_column(self, df, date_col):
        try:
            df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d')
            #df['Day'] = df[date_col].dt.day_name()
            df.insert(2, 'Day', df[date_col].dt.day_name())
        except Exception as e:
            print(f"Error parsing dates: {str(e)}")
        return df

    def add_rate_column(self, df):
        rates = []
        for _, row in df.iterrows():
            if row['user'] == 'Aminata':
                if row['Day'] == 'Sunday':
                    rates.append(16.5)
                elif row['Day'] == 'Saturday':
                    rates.append(15.5)
                else:
                    rates.append(14.5)
            elif row['user'] in ['Cito', 'Moradeyo']:
                if row['Day'] == 'Sunday':
                    rates.append(16)
                elif row['Day'] == 'Saturday':
                    rates.append(15)
                else:
                    rates.append(14)
            else:
                if row['Day'] == 'Sunday':
                    rates.append(14.5)
                elif row['Day'] == 'Saturday':
                    rates.append(13.5)
                else:
                    rates.append(12)
        df['Rate'] = rates
        return df


class ClearTimeSheetsView(View):
    def post(self, request):
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            TimeSheet.objects.filter(date_of_work__range=[start_date, end_date]).delete()
            return redirect('weekly_report')
        except Exception as e:
            return redirect('weekly_report')
