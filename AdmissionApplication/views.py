from django.shortcuts import render
from django.views.generic.edit import CreateView
from .models import User

# Create your views here.

class UserAddView(CreateView):
    model = User
    fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission")
    template_name = 'AdmissionApplication/admission.html'
    success_url = 'admission'