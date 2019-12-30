from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView,UpdateView
from .models import User
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from .forms import UserEntranceLogin
# Create your views here.
def MenuView(request):
    return render(request, 'AdmissionApplication/menu.html')

class UserAddView(CreateView):
    model = User
    fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission",)
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
        
class UserList(ListView):
    model = User

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        user.save()
        return HttpResponseRedirect(reverse('list')) 
    


class UserEntrance(TemplateView):    
    model=User
    template_name = 'AdmissionApplication/entrance.html'
    def post(self, request, *args, **kwargs):
        application_number = self.request.POST.get('application_number')   
        if  User.objects.all().filter(pk=application_number) :
            return HttpResponseRedirect(reverse('entrancewithID', args=(application_number,)))
        else :
            return HttpResponseRedirect(reverse('entrance'))
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserEntranceLogin()
        return context    

class UserEntranceWithIDView(UpdateView):
    model = User
    fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number")
    template_name = 'AdmissionApplication/entrancewithID.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserEntranceLogin()
        return context