
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
from django.contrib import messages
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak




class MonthlyReportView(View):
    template_name = 'agency/invoice.html'

    def get(self, request):
        # Generating month date ranges for the current year for selection
        current_year = datetime.now().year
        years = [current_year - 1, current_year, current_year + 1]
        months = {i: calendar.month_name[i] for i in range(1, 13)}

        context = {
            'years': years,
            'months': months,
            'current_year': current_year,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get('action')

        if action == 'generate_report':
            return self.generate_report(request)
        elif action == 'process_report':
            return self.process_report(request)
        # elif action == 'clear_timesheets':
        #     return self.clear_timesheets(request)

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

        # counter = 1
        # while os.path.exists(file_path):
        #     file_path = os.path.join(generated_reports_dir, 'Monthly_timesheet_unprocessed', f"monthly_report_{year}_{month_number}.csv")
        #     counter += 1

        try:
            os.makedirs(os.path.join(generated_reports_dir, 'Monthly_timesheet_unprocessed'), exist_ok=True)

            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['timesheet_id', 'user', 'date_of_work', 'shift_started_time', 'break_started_time', 'break_finished_time', 'shift_finished_time', 'client_rep_name', 'client_rep_position', 'care_home_name', 'staff_signature_image', 'client_rep_signature_image', 'total_hours_worked', 'total_amount']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for timesheet in timesheets:
                    care_home_name = timesheet.care_home_name
                    # care_home_first_name = care_home_user.first_name if care_home_user else 'N/A'

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
                        'care_home_name': care_home_name,
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
        year = int(request.POST.get('year'))
        month_number = int(request.POST.get('month_number'))

        start_date, end_date = self.get_month_date_range(year, month_number)
        timesheets = TimeSheet.objects.filter(
            date_of_work__gte=start_date,
            date_of_work__lte=end_date
        ).order_by('care_home_name', 'date_of_work')

        base_file_name = f"monthly_report_{year}_{month_number}.csv"
        generated_reports_dir = settings.GENERATED_REPORTS_DIR
        file_path = os.path.join(generated_reports_dir, 'Monthly_timesheet_unprocessed', base_file_name)

        # Finding the correct file path
        counter = 1
        while not os.path.exists(file_path) and counter < 100:
            file_path = os.path.join(generated_reports_dir, 'Monthly_timesheet_unprocessed', 
                                    f"monthly_report_{year}_{month_number}_{counter}.csv")
            counter += 1

        if not os.path.exists(file_path):
            return HttpResponseBadRequest('Generated report file not found.')

        try:
            # Reading the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)

            df = self.convert_times(df, 'shift_started_time', 'shift_finished_time')
            df['date_time_of_work'] = pd.to_datetime(df['date_of_work'])
            df = MonthlyReportView.add_weekday_column(df, 'date_of_work')
            df['invoice_rate'] = df['date_time_of_work'].apply(self.calculate_invoice_rate)

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
            columns_to_drop = ['s_no','client_rep_signature_image','staff_signature_image','total_hours_worked', 
                            'total_amount','break_started_time', 'break_finished_time', 'client_rep_name', 
                            'client_rep_position']
            df = df.drop(columns=columns_to_drop, errors='ignore')

            invoice_total = df.groupby(['care_home_name'], as_index=False).agg({
                'invoice_amount': 'sum'
            })

            subtotal = invoice_total.groupby(['care_home_name'])['invoice_amount'].sum().reset_index()
            final_output = df[['care_home_name','staff_name', 'date_of_work','day_name', 
                            'shift_started_time', 'shift_finished_time','worked_hours',
                            'invoice_rate','invoice_amount']].copy()

            final_output = pd.concat([final_output, subtotal], ignore_index=True, sort=False)
            final_output = final_output.sort_values(by=['care_home_name','date_of_work','staff_name'])

            # Create directories if they don't exist
            processed_invoice_dir = os.path.join(generated_reports_dir, 'processed_invoice')
            pdf_reports_dir = os.path.join(generated_reports_dir, 'PDF_reports')

            os.makedirs(processed_invoice_dir, exist_ok=True)
            os.makedirs(pdf_reports_dir, exist_ok=True)

            # Saving processed DataFrame back to CSV
            output_file = f"invoice_{year}_{month_number}_{counter}.csv"
            output_path = os.path.join(processed_invoice_dir, output_file)
            final_output.fillna('', inplace=True)

            final_output['date_of_work'] = final_output['date_of_work'].where(final_output['date_of_work'].notna(), '')  # Replace NaT
            final_output['date_of_work'] = final_output['date_of_work'].dt.strftime('%Y-%m-%d')            
            final_output.to_csv(output_path, index=False)
            final_output.fillna('Invoice Total', inplace=True)


            # Create a PDF in landscape A4 orientation
            output_pdf_file = f"invoice_{year}_{month_number}_{counter}.pdf"
            output_pdf_path = os.path.join(pdf_reports_dir, output_pdf_file)

            buffer = BytesIO()
            pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=100, leftMargin=100, 
                                    topMargin=30, bottomMargin=30)

            elements = []
            styles = getSampleStyleSheet()
            month_name = calendar.month_name[month_number]

            # Group by care home and create separate tables
            for care_home, group in final_output.groupby('care_home_name'):
                elements.append(Paragraph(f'Invoice Report for {year}-{month_name}', styles['Title']))
                elements.append(Paragraph(care_home, styles['Heading1']))
                group_data = [group.columns.tolist()] + group.values.tolist()
                
                col_widths = [1.5 * inch] * len(group.columns)
                col_widths[1] = 2.0 * inch
                for i in range(6, len(col_widths)):
                    col_widths[i] = 1.0 * inch
                for i in range(2, 6):
                    col_widths[i] = 1.2 * inch

                group_table = Table(group_data, colWidths=col_widths, rowHeights=[30] * len(group_data))

                # Set the style for group tables
                group_table.setStyle(TableStyle([
                    ('WORD_WRAP', (0, 0), (-1, -1), True),  # Enable word wrap for all cells
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica', 8),
                    ('ROWHEIGHT', (0, 0), (-1, -1), 35),  # Attempt to increase row height
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text at the top of the cell
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
     
                elements.append(group_table)
                elements.append(PageBreak())

            pdf.build(elements)

            # Write the PDF to the output path
            with open(output_pdf_path, 'wb') as f:
                f.write(buffer.getvalue())

            buffer.close()

            # Returning the CSV file as a response
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(output_path)}'
                return response

        except KeyError:
            return HttpResponseBadRequest('File not found in request.')
        except Exception as e:
            return HttpResponseBadRequest(f'Error processing file: {str(e)}')





class ClearTimeSheetsView(View):
    template_name = 'agency/clear_timesheets.html'

    def post(self, request):
        year = int(request.POST.get('year'))
        month_number = int(request.POST.get('month_number'))

        start_date, end_date = self.get_month_date_range(year, month_number)

        try:
            # Delete the timesheets within the specified date range
            TimeSheet.objects.filter(date_of_work__range=[start_date, end_date]).delete()
            messages.success(request, 'Timesheets cleared successfully.')
        except Exception as e:
            # Log the error and notify the user
            messages.error(request, f'Error clearing timesheets: {str(e)}')

        return redirect('clear_timesheets')

    def get_month_date_range(self, year, month):
        start_date = datetime(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime(year, month, last_day)
        return start_date, end_date

    def get(self, request):
        context = {
            'years': range(2024, datetime.now().year + 1),
            'months': {
                1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
        }
        return render(request, self.template_name, context)