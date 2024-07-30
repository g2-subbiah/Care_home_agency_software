# In your views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from staff.models import PersonalDetails, DocumentsCollection
from Agency.templatetags.custom_filters import expiry_status

@login_required
def profile_section(request):
    # Get the logged-in user's first and last name
    first_name = request.user.first_name
    last_name = request.user.last_name

    # Fetch the personal details for the user with status 'A'
    selected_staff = get_object_or_404(PersonalDetails, first_name=first_name, last_name=last_name, status='A')
    documents_collection = DocumentsCollection.objects.filter(personal_details=selected_staff).first()

    documents = {}
    if documents_collection:
        documents = {
            'Passport': {
                'document_number': documents_collection.passport_number,
                'document_date': documents_collection.passport_date,
                'expiry_date': documents_collection.passport_expiry_date,
                'expiry_status': expiry_status(documents_collection.passport_expiry_date)
            },
            'BRP': {
                'document_number': documents_collection.brp_number,
                'document_date': documents_collection.brp_date,
                'expiry_date': documents_collection.brp_expiry_date,
                'expiry_status': expiry_status(documents_collection.brp_expiry_date)
            },
            'Training Certificate': {
                'document_number': documents_collection.training_number,
                'document_date': documents_collection.training_date,
                'expiry_date': documents_collection.training_expiry_date,
                'expiry_status': expiry_status(documents_collection.training_expiry_date)
            },
            'DBS': {
                'document_number': documents_collection.dbs_number,
                'document_date': documents_collection.dbs_date,
                'expiry_date': documents_collection.dbs_expiry_date,
                'expiry_status': expiry_status(documents_collection.dbs_expiry_date)
            }
        }

    return render(request, 'staff/profile_section.html', {
        'selected_staff': selected_staff,
        'documents': documents,
    })
