from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from .models import User
from .forms import *
from django.views.generic.base import TemplateView
from django.utils import timezone
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, EmailMessage
from django.template.loader import get_template
import re
from django.db import models
from Team5.wsgi import application
from django.contrib.admin.utils import lookup_field
from unicodedata import lookup
# Create your views here.

phone_regex = re.compile(r'''(
    (0)
    (\d{1,3})
    (-)
    (\d{1,4})
    (-)
    (\d{3,4})
    )''', re.VERBOSE)

def MenuView(request):
    return render(request, 'AdmissionApplication/menu.html')

class UserAddView(CreateView):
    model = User
    #fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission", "password")
    form_class = ApplicationForm
    template_name = 'AdmissionApplication/admission.html'
    #success_url = '../menu_test'
    
    def post(self, request, *args, **kwargs):
        
        return CreateView.post(self, request, *args, **kwargs)
    
    def form_valid(self, form):
        ctx = {'form': form}
        if self.request.POST.get('next', '') == 'confirm':
            phone_serch = re.search(phone_regex, self.request.POST.get("phone_number"))
            if 'None' in str(phone_serch):
                return render(self.request, 'AdmissionApplication/warning_phone.html', ctx)
            elif (re.match('[A-Za-z0-9\._+]+@[A-Za-z]+\.[A-Za-z]', self.request.POST.get("mail_address")) == None) :
                return render(self.request, 'AdmissionApplication/warning_mail.html', ctx)      
            elif self.request.POST.get("entrance_schedule") > self.request.POST.get("exit_schedule"):# or self.request.POST.get("entrance_schedule") < self.request.POST.get("applecation_date"):
                return render(self.request, 'AdmissionApplication/warning_schedule.html', ctx)
            else:
                return render(self.request, 'AdmissionApplication/confirm.html', ctx)
            
        if self.request.POST.get('next', '') == 'back':
            return render(self.request, 'AdmissionApplication/admission.html', ctx)      
         
        if self.request.POST.get('next', '') == 'create':
            template = get_template('admissionapplication/mail/create_mail.html')
            mail_ctx={
                'user_name': form.cleaned_data['user_name'],
                'organization_name': form.cleaned_data['organization_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'mail_address': form.cleaned_data['mail_address'],
                'entrance_schedule': form.cleaned_data['entrance_schedule'],
                'exit_schedule': form.cleaned_data['exit_schedule'],
                'purpose_of_admission': form.cleaned_data['purpose_of_admission'],
                'application_number': form.cleaned_data['user_name'],
                'password': form.cleaned_data['user_name'],
                }
            EmailMessage(
                subject='入館申請完了',
                body=template.render(mail_ctx),
                to=[form.cleaned_data['mail_address']],
#                cc=[],
#                bcc=[],
            ).send()
            return super().form_valid(form)
                
def ResultView(request, **kwargs):
    return render(request, 'admissionapplication/result.html',{
        'contents': kwargs,
    })

class UserList(ListView):
    model = User

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        user.save()
        return HttpResponseRedirect(reverse('list')) 
    


class UserEntrance(TemplateView):    
    model=User
    fields = ("application_numbrer",)
    template_name = 'AdmissionApplication/entrance.html'
    form_class = UserEntranceForm
    #lookup_field='application_number'
    def post(self, request, *args, **kwargs):
        application_number = self.request.POST.get("application_number")
        s=False
        for a in User.objects.values_list("application_number",flat=True ):
            if int(a)==int(application_number):
                s=True

                break
        user = get_object_or_404(User, application_number=application_number)  
        pk=user.pk  
        if s==True : #s==True:#User.objects.filter(application_number=application_number):#User.objects.filter(application_number=application_number) :#User.objects.values_list("application_number",flat=True).get(pk=application_number) :#User.objects.all().filter(pk=application_number): 
            s=False
            return HttpResponseRedirect(reverse('entrancewithID', kwargs={'pk':pk}))
        elif s==False :
            return HttpResponseRedirect(reverse('entrance'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserEntranceForm()
        return context    

      
class UserEntranceWithIDView(UpdateView):
    model = User
    fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number")
    template_name = 'AdmissionApplication/entrancewithID.html'
    def post(self, request, *args, **kwargs):
        if self.request.POST.get('next', '') == 'entrance_time_save':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            user.achivement_entrance=timezone.now()
            user.save()
            return HttpResponseRedirect(reverse('entrance'))
        elif self.request.POST.get('next', '') == 'exit_time_save':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            user.achivement_exit=timezone.now()
            user.save()
            return HttpResponseRedirect(reverse('entrance'))
        else:
            return HttpResponseRedirect(reverse('entrance'))

class UserShowWithIDView(UpdateView):
    model = User
    fields = ('application_number','user_name', 'organization_name', 'phone_number', 'mail_address', 'purpose_of_admission')
    template_name = 'AdmissionApplication/user_list_detail.html'
    success_url = 'list/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserIdForm(initial = {'user_id' : self.kwargs.get('pk')})
        return context    

