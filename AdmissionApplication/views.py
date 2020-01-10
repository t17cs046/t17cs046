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
import re, string, random
from datetime import datetime
from django.db import models
from Team5.wsgi import application
from django.contrib.admin.utils import lookup_field
from unicodedata import lookup
from django.core import mail
from django.contrib import messages
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

    def form_valid(self, form):
        ctx = {'form': form}
        if form.is_valid():
            word = string.digits + string.ascii_lowercase + string.ascii_uppercase
            user = form.save(commit=False)
            user.application_number = random.randrange(999) + int(datetime.now().strftime('%y')) * 100000 + int(datetime.now().strftime('%m')) * 1000
            user.password = ''.join([random.choice(word) for i in range(8)])
            
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
            user = form.save(commit=False)
            template = get_template('AdmissionApplication/mail/create_mail.html')
            mail_ctx={
                'user_name': form.cleaned_data['user_name'],
                'organization_name': form.cleaned_data['organization_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'mail_address': form.cleaned_data['mail_address'],
                'entrance_schedule': form.cleaned_data['entrance_schedule'],
                'exit_schedule': form.cleaned_data['exit_schedule'],
                'purpose_of_admission': form.cleaned_data['purpose_of_admission'],
                'application_number': user.application_number,
                'password': user.password,
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
    return render(request, 'AdmissionApplication/result.html',{
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
    def post(self, request, *args, **kwargs):
        application_number = self.request.POST.get("application_number")
        user = get_object_or_404(User, application_number=application_number)  
        pk=user.pk  
        return HttpResponseRedirect(reverse('entrancewithID', kwargs={'pk':pk}))

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
    
    

class UserChangeDeleteView(TemplateView):    
    model=User
    fields = ("application_numbrer",)
    template_name = 'AdmissionApplication/changedelete.html'
    form_class = UserChangeDeleteForm
    def post(self, request, *args, **kwargs):
        application_number = self.request.POST.get("application_number")
        password = self.request.POST.get("password")
        user = get_object_or_404(User, application_number=application_number)  
        pk=user.pk  
        if(user.password ==password):
            return HttpResponseRedirect(reverse('changedeleteshowwithID', kwargs={'pk':pk}))
        else: 
            messages.info(self.request,'申請番号かパスワードが間違っています.')
            return HttpResponseRedirect(reverse('changedelete'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserChangeDeleteForm()
        return context    
    
class UserChangeDeleteShowWithIDView(UpdateView):
    model = User
    fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number")
    template_name = 'AdmissionApplication/changedeleteshowwithID.html'
    def post(self, request, *args, **kwargs):
        if self.request.POST.get('next', '') == 'change':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            pk = user.pk
            return HttpResponseRedirect(reverse('changewithID', kwargs={'pk':pk}))
        elif self.request.POST.get('next', '') == 'delete':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            pk=user.pk
            return HttpResponseRedirect(reverse('deletewithID', kwargs={'pk':pk}))
        elif self.request.POST.get('next', '') == 'back':
            return HttpResponseRedirect(reverse('changedelete'))
        else:
            return HttpResponseRedirect(reverse('changedeleteshowwidhID'))


class UserChangeWithIDView(UpdateView):
    model = User
    #fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number")
    template_name = 'AdmissionApplication/changewithID.html'
    form_class = ApplicationForm
    success_url = '../menu_test'
    '''
    def post(self,request, *args, **kwargs):
        if self.request.POST.get('next', '') == 'change':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            name = self.request.POST.get('user_name')
            organization_name=self.request.POST.get('organization_name')
            phone_number = self.request.POST.get('phone_number')
            mail_address = self.request.POST.get('mail_addres')
            entrance_schedule = self.request.POST.get('entrance_schedule')
            exit_schedule = self.request.POST.get('exit_schedule')
            purpose_of_admission = self.request.POST.get('purpose_of_admission')
            password = self.request.POST.get('password')
            user.user_name=name
            user.organization_name = organization_name
            user.phone_number = phone_number
            user.mail_addres = mail_address
            user.entrance_schedule = entrance_schedule
            user.exit_schedule = exit_schedule
            user.purpose_of_admission = purpose_of_admission
            pk=user.pk
            if(user.approval == True):
                messages.info(self.request,'承認済のため修正できません.')
                return HttpResponseRedirect(reverse('changewithID', kwargs={'pk':pk}))
            if(user.password != password):
                messages.info(self.request,'パスワードが間違っています.')
                return HttpResponseRedirect(reverse('changewithID', kwargs={'pk':pk}))
            user.save()
            return HttpResponseRedirect(reverse('changedelete'))
        elif self.request.POST.get('next', '') == 'back':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            pk=user.pk
            return HttpResponseRedirect(reverse('changedeleteshowwithID',kwargs={'pk':pk}))
        else:
            return HttpResponseRedirect(reverse('changedelete'))
            '''
    def form_valid(self, form):
        ctx = {'form': form}
        if self.request.POST.get('next', '') == 'confirm':
            user=form.save(commit=False)
            pk=user.pk
            password=self.request.POST.get('password')
            if(user.approval == True):
                messages.info(self.request,'承認済のため修正できません.')
                return HttpResponseRedirect(reverse('changewithID', kwargs={'pk':pk}))
            if(user.password != password):
                messages.info(self.request,'パスワードが間違っています.')
                return HttpResponseRedirect(reverse('changewithID', kwargs={'pk':pk}))
            return render(self.request, 'AdmissionApplication/changeconfirm.html', ctx)
        if self.request.POST.get('next', '') == 'back_show':
            user=form.save(commit=False)
            pk=user.pk
            return HttpResponseRedirect(reverse('changedeleteshowwithID', kwargs={'pk':pk}))  
        if self.request.POST.get('next', '') == 'back_change':
            return render(self.request, 'AdmissionApplication/changewithID.html', ctx) 
        if self.request.POST.get('next', '') == 'change':
            user = form.save(commit=False)
            user.save()
            template = get_template('AdmissionApplication/mail/change_mail.html')
            mail_ctx={
                'user_name': form.cleaned_data['user_name'],
                'organization_name': form.cleaned_data['organization_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'mail_address': form.cleaned_data['mail_address'],
                'entrance_schedule': form.cleaned_data['entrance_schedule'],
                'exit_schedule': form.cleaned_data['exit_schedule'],
                'purpose_of_admission': form.cleaned_data['purpose_of_admission'],
                'application_number': user.application_number,
                'password': user.password,
                }
            EmailMessage(
                subject='入館申請情報修正完了',
                body=template.render(mail_ctx),
                to=[form.cleaned_data['mail_address']],
#                cc=[],
#                bcc=[],
            ).send()
            return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] =  ApplicationForm(initial = {'user_id' : self.kwargs.get('pk')})
        context.update({
            #'password_form': UserPasswordForm(**self.get_form_kwargs()),
            'password_form': UserPasswordForm(initial = {'password' : ''})
            })
        return context
    
class UserDeleteWithIDView(UpdateView): 
    model = User
    #fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number")
    template_name = 'AdmissionApplication/deletewithID.html'
    form_class = UserPasswordForm
    def post(self, request, *args, **kwargs):
        if self.request.POST.get('next', '') == 'back':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            pk=user.pk
            return HttpResponseRedirect(reverse('changedeleteshowwithID', kwargs={'pk':pk}))
      
        elif self.request.POST.get('next', '') == 'delete':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            password = self.request.POST.get('password')
            pk=user.pk
            if(user.approval == True):
                messages.info(self.request,'承認済のため削除できません.')
                return HttpResponseRedirect(reverse('deletewithID', kwargs={'pk':pk}))
            if(user.password != password):
                messages.info(self.request,'パスワードが間違っています.')
                return HttpResponseRedirect(reverse('deletewithID', kwargs={'pk':pk}))
            else:
                template = get_template('AdmissionApplication/mail/delete_mail.html')
                mail_ctx={
                'user_name': user.user_name,
                'organization_name': user.organization_name,
                'phone_number': user.phone_number,
                'mail_address': user.mail_address,
                'entrance_schedule': user.entrance_schedule,
                'exit_schedule': user.exit_schedule,
                'purpose_of_admission': user.purpose_of_admission,
                'application_number': user.application_number,
                    }
                EmailMessage(
                    subject='入館申請情報削除完了',
                    body=template.render(mail_ctx),
                    to=[user.mail_address],
#                    cc=[],
#                    bcc=[],
                ).send()
                user.delete()
                return HttpResponseRedirect(reverse('changedelete'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] =  ApplicationForm(initial = {'user_id' : self.kwargs.get('pk')})
        context['form'] = UserPasswordForm()
        return context   