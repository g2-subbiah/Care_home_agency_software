import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .forms import PersonalDetailsForm, DocumentsCollectionForm, DocumentsCollection
from django.http import HttpResponse


class FileUploadView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        file = request.FILES.get('file')
        doc_type = request.POST.get('doc_type')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if not all([file, doc_type, first_name, last_name]):
            return JsonResponse({'message': 'Missing required fields'}, status=400)

        save_document(file, first_name, last_name, doc_type)
        return JsonResponse({'message': f'{doc_type} document uploaded successfully!'})

def new_staff(request):
    if request.method == 'POST':
        personal_form = PersonalDetailsForm(request.POST)
        documents_form = DocumentsCollectionForm(request.POST, request.FILES)

        if personal_form.is_valid():
            personal_details = personal_form.save()
            
            # Process documents form
            if documents_form.is_valid():
                documents_data = documents_form.cleaned_data
                # Create or update the related DocumentsCollection object
                documents_collection, created = DocumentsCollection.objects.get_or_create(
                    personal_details=personal_details,
                    defaults={
                        'passport_number': documents_data.get('passport_document_number'),
                        'passport_date': documents_data.get('passport_document_date'),
                        'passport_expiry_date': documents_data.get('passport_document_expiry_date'),
                        'brp_number': documents_data.get('brp_document_number'),
                        'brp_date': documents_data.get('brp_document_date'),
                        'brp_expiry_date': documents_data.get('brp_document_expiry_date'),
                        'training_number': documents_data.get('training_document_number'),
                        'training_date': documents_data.get('training_document_date'),
                        'training_expiry_date': documents_data.get('training_document_expiry_date'),
                        'dbs_number': documents_data.get('dbs_document_number'),
                        'dbs_date': documents_data.get('dbs_document_date'),
                        'dbs_expiry_date': documents_data.get('dbs_document_expiry_date'),
                    }
                )
                if not created:
                    # Update the existing DocumentsCollection object
                    for field, value in documents_data.items():
                        setattr(documents_collection, field, value)
                    documents_collection.save()
            else:
                # Return with form errors
                return HttpResponse(f"Documents collection form errors: {documents_form.errors}", status=400)
            
            # Handle file uploads if needed
            files = request.FILES
            doc_types = ['passport', 'brp', 'training', 'dbs']
            for doc_type in doc_types:
                if doc_type + '_upload' in files:
                    file = files[doc_type + '_upload']
                    save_document(file, personal_details.first_name, personal_details.last_name, doc_type)
                
            return redirect('success_application')
        else:
            # Return with form errors
            return HttpResponse(f"Personal details form errors: {personal_form.errors}", status=400)
    
    else:
        personal_form = PersonalDetailsForm()
        documents_form = DocumentsCollectionForm()

    return render(request, 'staff/new_staff.html', {'personal_form': personal_form, 'documents_form': documents_form})

def save_document(file, first_name, last_name, doc_type):
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GENERATED_REPORTS_DIR = os.path.join(BASE_DIR, 'generated_reports')
    folder_name = f"{first_name}_{last_name}"
    folder_path = os.path.join(GENERATED_REPORTS_DIR, 'staff_documents', folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{doc_type}_{file.name}")
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def success(request):
    return render(request, 'staff/success_application.html')