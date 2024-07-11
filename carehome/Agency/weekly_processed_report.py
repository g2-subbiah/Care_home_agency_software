import csv
import os
import pandas as pd
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from staff.models import WeekDateRange, TimeSheet
from django.conf import settings
from .models import CustomUser
from django.db.models import Value as V
from django.db.models.functions import Concat


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
        elif action == 'process_pay_detail':
                pay_details_response = self.generate_pay_details(request)
                return pay_details_response  # Returns the generated pay details response
        else:
            return HttpResponseBadRequest('Invalid action')
        
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

        # # Checking if the file already exists, if yes, append a number to make it unique
        # counter = 1
        # while os.path.exists(file_path):
        #     file_path = os.path.join(generated_reports_dir, 'Weekly_timesheet_unprocessed', f"weekly_report_week_{week_number}_{counter}.csv")
        #     counter += 1

        try:
            os.makedirs(os.path.join(generated_reports_dir, 'Weekly_timesheet_unprocessed'), exist_ok=True)

            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['user', 'date_of_work', 'shift_started_time', 'break_started_time', 'break_finished_time', 'shift_finished_time', 'client_rep_name', 'client_rep_position', 'care_home_name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for timesheet in timesheets:
                    # Fetching the care home name's first name
                    care_home_user = timesheet.care_home_name
                    care_home_first_name = care_home_user.first_name if hasattr(care_home_user, 'first_name') else care_home_user
                    
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

            return HttpResponse(f'Success! CSV file generated and saved at {file_path}')
        
        except Exception as e:
            # Logging the exception or handle it appropriately
            print(f"Error generating report: {e}")
            return HttpResponse(f'Error generating report: {e}', status=500)

    def process_report(self, request):
        year = request.POST.get('year')
        week_number = request.POST.get('week_number')

        base_file_name = f"weekly_report_week_{week_number}.csv"
        generated_reports_dir = settings.GENERATED_REPORTS_DIR
        file_path = os.path.join(generated_reports_dir, 'Weekly_timesheet_unprocessed', base_file_name)

        # Finding the correct file path
        counter = 1
        while not os.path.exists(file_path) and counter < 100:
            file_path = os.path.join(generated_reports_dir, 'Weekly_timesheet_unprocessed', f"weekly_report_week_{week_number}_{counter}.csv")
            counter += 1

        if not os.path.exists(file_path):
            return HttpResponseBadRequest('Generated report file not found.')

        try:
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
            existing_columns = df.columns.tolist()

            if 'care_home_name' in existing_columns:
                existing_columns.remove('care_home_name')
                existing_columns.append('care_home_name')

            df = df[existing_columns]

            columns_to_drop = ['break_started_time', 'break_finished_time', 'client_rep_name', 'client_rep_position']
            df = df.drop(columns=columns_to_drop, errors='ignore')

            # Creating the directory for processed reports if it doesn't exist
            try:
                os.makedirs(os.path.join(generated_reports_dir, 'Weekly_processed_reports'), exist_ok=True)
            except OSError as e:
                # Handling the error (log it, raise it, etc.)
                print(f"Error creating directory: {e}")

            # Saving processed DataFrame back to CSV
            output_path = os.path.join(generated_reports_dir, 'Weekly_processed_reports', 'processed_' + os.path.basename(file_path))
            df.to_csv(output_path, index=False)

            # Returning the processed CSV file as a response
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(output_path)}'
                return response

        except Exception as e:
            return HttpResponseBadRequest(f'Error processing file: {str(e)}')
        
    def generate_pay_details(self, request):
        year = request.POST.get('year')
        week_number = request.POST.get('week_number')

        base_file_name = f"processed_weekly_report_week_{week_number}.csv"
        generated_reports_dir = settings.GENERATED_REPORTS_DIR
        file_path = os.path.join(generated_reports_dir, 'Weekly_processed_reports', base_file_name)

        # Finding the correct file path
        counter = 1
        while not os.path.exists(file_path) and counter < 100:
            file_path = os.path.join(generated_reports_dir, 'Weekly_processed_reports', f"processed_weekly_report_week_{week_number}_{counter}.csv")
            counter += 1

        if not os.path.exists(file_path):
            return HttpResponseBadRequest('Generated report file not found.')

        try:
            # Reading the CSV file into a DataFrame
            weekly_rep = pd.read_csv(file_path)
            #weekly_rep = self.process_report(df)

            # Calculating Payment amount(£) for each row
            weekly_rep['Payment amount(£)'] = (weekly_rep['Rate'] * weekly_rep['working_hours']).round(2)

            # Fetching staff_name and username from CustomUser entries
            staff_ids = []
            for index, row in weekly_rep.iterrows():
                staff_name = row['staff_name']
                try:
                    # Querying CustomUser based on concatenated first_name and last_name
                    user = CustomUser.objects.annotate(
                        full_name=Concat('first_name', V(' '), 'last_name')
                    ).get(full_name__iexact=staff_name)
                    staff_ids.append(user.username)
                except CustomUser.DoesNotExist:
                    # Handling case where CustomUser does not exist for given first_name and last_name
                    staff_ids.append('Unknown')

            # Assigning the fetched usernames to the DataFrame and rename to 'staff_id'
            weekly_rep['staff_id'] = staff_ids

            # Grouping by staff_id, staff_name, Rate and calculate total working_hours and Payment amount(£)
            pay_details = weekly_rep.groupby(['staff_id', 'staff_name', 'Rate'], as_index=False).agg({
                'working_hours': 'sum',
                'Payment amount(£)': 'sum'
            })

            # Calculating subtotal (total payment amount) for each staff_id
            subtotal = pay_details.groupby(['staff_id', 'staff_name'])['Payment amount(£)'].sum().reset_index()
            subtotal = subtotal.rename(columns={'Payment amount(£)': 'Total Payment amount(£)'})

            # Rearranging columns: put 'working_hours' in front of 'Rate'
            final_output = pay_details[['staff_id', 'staff_name', 'working_hours', 'Rate', 'Payment amount(£)']].copy()

            # Appending subtotal rows at the end of each staff member's section
            final_output = pd.concat([final_output, subtotal], ignore_index=True, sort=False)

            # Sorting the final_output by staff_id, staff_name, and then by Rate
            final_output = final_output.sort_values(by=['staff_id', 'staff_name', 'Rate'])

            # Creating the directory for processed pay details if it doesn't exist
            generated_reports_dir = settings.GENERATED_REPORTS_DIR
            os.makedirs(os.path.join(generated_reports_dir, 'Weekly_pay_details'), exist_ok=True)

            # Saving pay details DataFrame to CSV
            output_filename = f"pay_detail_week_{week_number}.csv"
            pay_details_output_path = os.path.join(generated_reports_dir, 'Weekly_pay_details', 'pay_details_' + os.path.basename(output_filename))
            final_output.to_csv(pay_details_output_path, index=False)

            # Returning the pay details CSV file as a response
            with open(pay_details_output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(pay_details_output_path)}'
                return response

        except Exception as e:
            return HttpResponseBadRequest(f'Error generating pay details: {str(e)}')


    def add_weekday_column(self, df, date_col):
        try:
            df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d')
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
            elif row['user'] in ['Cito','Moradeyo']:
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
