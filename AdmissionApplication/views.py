from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView
from .models import User
from django.views.generic.base import TemplateView

# Create your views here.
def MenuView(request):
    return render(request, 'AdmissionApplication/menu.html')

class UserAddView(CreateView):
    model = User
    fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission")
    template_name = 'AdmissionApplication/admission.html'
    success_url = '../menu_test'
    
    def form_valid(self, form):
        ctx = {'form': form}
        if self.request.POST.get('next', '') == 'confirm':
            return render(self.request, 'AdmissionApplication/confirm.html', ctx)
        if self.request.POST.get('next', '') == 'back':
            return render(self.request, 'AdmissionApplication/admission.html', ctx)
        if self.request.POST.get('next', '') == 'create':
            return super().form_valid(form)