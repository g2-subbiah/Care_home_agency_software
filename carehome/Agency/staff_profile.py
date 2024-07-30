from django.shortcuts import render, get_object_or_404
from staff.models import PersonalDetails, DocumentsCollection
from .templatetags.custom_filters import expiry_status

def staff_profile(request):
    staff_id = request.GET.get('staff_id')
    selected_staff = None
    documents = {}

    # Filter staff list to include only approved staff
    staff_list = PersonalDetails.objects.filter(status='A')

    if staff_id:
        selected_staff = get_object_or_404(PersonalDetails, id=staff_id)
        documents_collection = DocumentsCollection.objects.filter(personal_details=selected_staff).first()
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

    return render(request, 'agency/staff_profile.html', {
        'staff_list': staff_list,
        'selected_staff': selected_staff,
        'documents': documents,
    })
