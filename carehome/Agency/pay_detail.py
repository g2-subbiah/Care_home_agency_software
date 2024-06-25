import os
import pandas as pd
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.views import View
from django.shortcuts import render
from .models import CustomUser
from django.db.models import Value as V
from django.db.models.functions import Concat


class PayDetailProcessView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'agency/pay_detail.html')

    def post(self, request, *args, **kwargs):
        try:
            if 'file' not in request.FILES:
                return HttpResponseBadRequest('File not found in request.')

            file = request.FILES['file']
            file_path = os.path.join(settings.MEDIA_ROOT, file.name)

            # Saving uploaded file
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Generating pay details
            pay_details_response = self.generate_pay_details(file_path)

            # Deleting the uploaded file after processing (optional)
            if os.path.exists(file_path):
                os.remove(file_path)

            return pay_details_response

        except Exception as e:
            return HttpResponseBadRequest(f'Error processing file: {str(e)}')

    def generate_pay_details(self, processed_file):
        try:
            # Reading the CSV file into a DataFrame
            weekly_rep = pd.read_csv(processed_file)

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
            try:
                os.makedirs(os.path.join(generated_reports_dir, 'Weekly_pay_details'), exist_ok=True)
            except OSError as e:
                # Handling the error (log it, raise it, etc.)
                print(f"Error creating directory: {e}")

            # Saving pay details DataFrame to CSV
            pay_details_output_path = os.path.join(generated_reports_dir, 'Weekly_pay_details', 'pay_details_' + os.path.basename(processed_file))
            final_output.to_csv(pay_details_output_path, index=False)

            # Returning the pay details CSV file as a response
            with open(pay_details_output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(pay_details_output_path)}'
                return response

        except Exception as e:
            return HttpResponseBadRequest(f'Error generating pay details: {str(e)}')
