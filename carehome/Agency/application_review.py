from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from staff.models import PersonalDetails, DocumentsCollection
import os
import shutil
from urllib.parse import urlencode

def list_applications(request):
    applications = PersonalDetails.objects.filter(status='P')
    return render(request, 'agency/pending_applications.html', {'applications': applications})

def application_detail(request, pk):
    personal_details = get_object_or_404(PersonalDetails, pk=pk)
    documents_collection = get_object_or_404(DocumentsCollection, personal_details=personal_details)

    return render(request, 'agency/application_detail.html', {
        'personal_details': personal_details,
        'documents_collection': documents_collection
    })

def approve_application(request, pk):
    personal_details = get_object_or_404(PersonalDetails, pk=pk)
    documents_collection = get_object_or_404(DocumentsCollection, personal_details=personal_details)

    # Update status to Approved
    personal_details.status = 'A'
    personal_details.save()

    # Create query parameters for the redirect URL
    query_params = urlencode({
        'first_name': personal_details.first_name,
        'last_name': personal_details.last_name,
        'email': personal_details.email_id
    })

    # Generate the URL for the register view
    register_url = reverse('register')

    # Redirect to registration page with applicant details
    return redirect(f'{register_url}?{query_params}')

def reject_application(request, pk):
    personal_details = get_object_or_404(PersonalDetails, pk=pk)
    documents_collection = get_object_or_404(DocumentsCollection, personal_details=personal_details)

    # Delete documents and personal details
    personal_details.delete()
    documents_collection.delete()

    # Optionally, delete files if needed
    folder_path = os.path.join('generated_reports', 'staff_documents', f"{personal_details.first_name}_{personal_details.last_name}")
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    return redirect('pending_applications')
