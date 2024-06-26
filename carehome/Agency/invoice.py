
import os
import csv
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views import View
from staff.models import TimeSheet
import pandas as pd
import calendar

class MonthlyReportView(View):
    template_name = 'agency/invoice.html'

    def get(self, request):
        # Generating month date ranges for the current year for selection
        current_year = datetime.now().year
        years = [current_year]  
        months = {i: calendar.month_name[i] for i in range(1, 13)}

        context = {
            'years': years,
            'months': months,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get('action')

        if action == 'generate_report':
            return self.generate_report(request)
        elif action == 'process_report':
            return self.process_report(request)
        elif action == 'clear_timesheets':
            return self.clear_timesheets(request)

    def convert_times(self, df, start_col, end_col):
        df[start_col] = pd.to_datetime(df[start_col]).dt.strftime('%H:%M')
        df[end_col] = pd.to_datetime(df[end_col]).dt.strftime('%H:%M')
        return df

    def get_month_date_range(self, year, month):
        start_date = datetime(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime(year, month, last_day)
        return start_date, end_date
    
    def calculate_invoice_rate(self, date):
        # Default rates
        weekday_rate = 21  # Monday to Friday
        weekend_rate = 25  # Saturday and Sunday

        # Checking if date is a weekend (Saturday or Sunday)
        if date.weekday() in [5, 6]:  # Saturday is 5, Sunday is 6
            return weekend_rate
        else:
            return weekday_rate
        
    def add_weekday_column(df, date_col):
        try:
            df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d')
            df['day_name'] = df[date_col].dt.strftime('%A')  # Adding a column with the full day name (e.g., Monday, Tuesday, etc.)
        except Exception as e:
            print(f"Error parsing dates: {str(e)}")
        return df

    def generate_report(self, request):
        year = int(request.POST.get('year'))
        month_number = int(request.POST.get('month_number'))

        start_date, end_date = self.get_month_date_range(year, month_number)
        timesheets = TimeSheet.objects.filter(
            date_of_work__gte=start_date,
            date_of_work__lte=end_date
        ).order_by('care_home_name', 'date_of_work')  # Ordered by care_home_name and date_of_work

        base_file_name = f"monthly_report_{year}_{month_number}.csv"
        generated_reports_dir = settings.GENERATED_REPORTS_DIR
        file_path = os.path.join(generated_reports_dir, 'Monthly_timesheet_unprocessed', base_file_name)

        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(generated_reports_dir, 'Monthly_timesheet_unprocessed', f"monthly_report_{year}_{month_number}_{counter}.csv")
            counter += 1

        try:
            os.makedirs(os.path.join(generated_reports_dir, 'Monthly_timesheet_unprocessed'), exist_ok=True)

            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['timesheet_id', 'user', 'date_of_work', 'shift_started_time', 'break_started_time', 'break_finished_time', 'shift_finished_time', 'client_rep_name', 'client_rep_position', 'care_home_name', 'staff_signature_image', 'client_rep_signature_image', 'total_hours_worked', 'total_amount']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for timesheet in timesheets:
                    care_home_user = timesheet.care_home_name
                    care_home_first_name = care_home_user.first_name if care_home_user else 'N/A'

                    # Calculating total hours worked
                    total_hours = (timesheet.shift_finished_time - timesheet.shift_started_time).total_seconds() / 3600

                    # Calculating invoice rate for the date
                    invoice_rate = self.calculate_invoice_rate(timesheet.date_of_work)

                    # Calculating total amount
                    total_amount = total_hours * invoice_rate

                    writer.writerow({
                        'timesheet_id': timesheet.id,
                        'user': timesheet.user.get_full_name(),
                        'date_of_work': timesheet.date_of_work,
                        'shift_started_time': timesheet.shift_started_time,
                        'break_started_time': timesheet.break_started_time,
                        'break_finished_time': timesheet.break_finished_time,
                        'shift_finished_time': timesheet.shift_finished_time,
                        'client_rep_name': timesheet.client_rep_name,
                        'client_rep_position': timesheet.client_rep_position,
                        'care_home_name': care_home_first_name,
                        'staff_signature_image': timesheet.staff_signature_image.url if timesheet.staff_signature_image else '',
                        'client_rep_signature_image': timesheet.client_rep_signature_image.url if timesheet.client_rep_signature_image else '',
                        'total_hours_worked': float(total_hours),
                        'total_amount': float(total_amount)
                    })

            return HttpResponse(f'Success! CSV file generated and saved at {file_path}')
        
        except Exception as e:
            # Logging the exception or handle it appropriately
            print(f"Error generating report: {e}")
            return HttpResponse(f'Error generating report: {e}', status=500)

    def process_report(self, request):
        try:
            file = request.FILES['file']
            file_path = os.path.join(settings.GENERATED_REPORTS_DIR, 'Monthly_timesheet_unprocessed', file.name)
            
            # Saving the uploaded file
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Reading the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)

            # Correctly calling the convert_times method using self
            df = self.convert_times(df, 'shift_started_time', 'shift_finished_time')
            df['date_of_work'] = pd.to_datetime(df['date_of_work'])
            df = MonthlyReportView.add_weekday_column(df,'date_of_work')
            df['invoice_rate'] = df['date_of_work'].apply(self.calculate_invoice_rate)

            # Calculate working hours
            df['worked_hours'] = (pd.to_datetime(df['shift_finished_time']) - pd.to_datetime(df['shift_started_time'])).dt.total_seconds() / 3600
            df['invoice_amount'] = df['worked_hours'] * df['invoice_rate']


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

            columns_to_drop = ['s_no','client_rep_signature_image','staff_signature_image','total_hours_worked', 'total_amount','break_started_time', 'break_finished_time', 'client_rep_name', 'client_rep_position']
            df = df.drop(columns=columns_to_drop, errors='ignore')

            invoice_total = df.groupby(['care_home_name'], as_index=False).agg({
                'invoice_amount': 'sum'
            })

            # Calculating subtotal (total payment amount) for each staff_id
            subtotal = invoice_total.groupby(['care_home_name'])['invoice_amount'].sum().reset_index()

            # Rearranging columns: put 'working_hours' in front of 'Rate'
            final_output = df[['care_home_name','timesheet_id', 'staff_name', 'date_of_work','day_name', 'shift_started_time', 'shift_finished_time','worked_hours','invoice_rate','invoice_amount']].copy()

            # Appending subtotal rows at the end of each care_home_name
            final_output = pd.concat([final_output, subtotal], ignore_index=True, sort=False)

            # Sorting the final_output by staff_id, staff_name, and then by Rate
            final_output = final_output.sort_values(by=['care_home_name','date_of_work','staff_name'])

            # Create the directory for processed reports if it doesn't exist
            generated_reports_dir = settings.GENERATED_REPORTS_DIR
            try:
                os.makedirs(os.path.join(generated_reports_dir, 'processed_invoice'), exist_ok=True)
            except OSError as e:
                # Handle the error (log it, raise it, etc.)
                print(f"Error creating directory: {e}")

            # Saving processed DataFrame back to CSV
            output_path = os.path.join(generated_reports_dir, 'processed_invoice', 'invoice_' + file.name)
            final_output.to_csv(output_path, index=False)

            # output_path_pdf = os.path.join(generated_reports_dir, 'processed_invoice', 'invoice_' + os.path.splitext(file.name)[0] + '.pdf')
            # html_content = final_output.to_html(index=False)
            # pdfkit.from_string(html_content, output_path_pdf)

            # Returning the processed CSV file as a response
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(output_path)}'
                return response

        except KeyError:
            return HttpResponseBadRequest('File not found in request.')
        except Exception as e:
            return HttpResponseBadRequest(f'Error processing file: {str(e)}')


class ClearTimeSheetsView(View):
    def post(self, request):
        year = int(request.POST.get('year'))
        month_number = int(request.POST.get('month_number'))

        start_date, end_date = self.get_month_date_range(year, month_number)

        try:
            TimeSheet.objects.filter(date_of_work__range=[start_date, end_date]).delete()
            return redirect('invoice')  
        except Exception as e:
            return redirect('invoice')  

    def get_month_date_range(self, year, month):
        start_date = datetime(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime(year, month, last_day)
        return start_date, end_date