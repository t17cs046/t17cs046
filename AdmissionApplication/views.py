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
from django.shortcuts import redirect
import re, string, random
from datetime import datetime
from django.db import models
from Team5.wsgi import application
from django.contrib.admin.utils import lookup_field
from unicodedata import lookup
from django.contrib import messages
from django.db.models import Q

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
            random_number=random.randrange(999) + int(datetime.now().strftime('%y')) * 100000 + int(datetime.now().strftime('%m')) * 1000
            while(User.objects.filter(application_number__exact=random_number).count() > 0):
                random_number = random.randrange(999) + int(datetime.now().strftime('%y')) * 100000 + int(datetime.now().strftime('%m')) * 1000
            user.application_number = random_number
            user.password = ''.join([random.choice(word) for i in range(8)])
            
        if self.request.POST.get('next', '') == 'confirm':
            phone_serch = re.search(phone_regex, self.request.POST.get("phone_number"))
            
            #承認済み利用者を取得
            all_entries = User.objects.filter(approval__exact="True")
            #氏名と異なる利用者を取得
            all_entries = all_entries.exclude(user_name=self.request.POST.get("user_name"))
            #組織名と異なる利用者を取得
            all_entries = all_entries.exclude(organization_name=self.request.POST.get("organization_name"))
            #自分の入館時間<他の利用者の退館時間<自分の退館時間
            overlapping_1 = all_entries.filter(exit_schedule__range=(self.request.POST.get("entrance_schedule"), self.request.POST.get("exit_schedule")))
            #自分の入館時間<他の利用者の入館時間<自分の退館時間
            overlapping_2 = all_entries.filter(entrance_schedule__range=(self.request.POST.get("entrance_schedule"),self.request.POST.get("exit_schedule")))
            #他の利用者の入館時間<自分の入館時間<自分の退館時間<他の利用者の退館時間
            overlapping_3 = all_entries.filter(entrance_schedule__lt=self.request.POST.get("entrance_schedule"))
            overlapping_3 = overlapping_3.filter(exit_schedule__gt=self.request.POST.get("exit_schedule"))

            today = str(datetime.now().year)+ '-' + str(datetime.now().month) +'-'+ str(datetime.now().day) + ' ' + str(datetime.now().hour) + ':' + str(datetime.now().minute) 
            print(today)
            if (re.match('[ｦ-ﾟ]', self.request.POST.get("user_name")) != None):
                return render(self.request, 'AdmissionApplication/warning/warning_name.html', ctx)
            
            elif 'None' in str(phone_serch):
                return render(self.request, 'AdmissionApplication/warning/warning_phone.html', ctx)
           
            elif (re.match('[A-Za-z0-9\._+]+@[A-Za-z]+\.[A-Za-z]', self.request.POST.get("mail_address")) == None) :
                return render(self.request, 'AdmissionApplication/warning/warning_mail.html', ctx)      
            
            elif self.request.POST.get("entrance_schedule") > self.request.POST.get("exit_schedule"):
                return render(self.request, 'AdmissionApplication/warning/warning_schedule.html', ctx)
            
            elif self.request.POST.get("entrance_schedule") < today:
                return render(self.request, 'AdmissionApplication/warning/warning_now_schedule.html', ctx)
            
            elif overlapping_1.count() > 0 or overlapping_2.count() > 0 or overlapping_3.count() > 0:
                return render(self.request, 'AdmissionApplication/warning/warning_other_schedule.html', ctx)
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
                bcc=['team05.m46@gmail.com'],
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
    
    def get_queryset(self):
        q_word = self.request.GET.get('query')
 
        if q_word:
            object_list = User.objects.filter(
                Q(organization_name__icontains=q_word))
        else:
            object_list = User.objects.all()
        return object_list 
    


class UserEntrance(TemplateView):    
    model=User
    fields = ("application_numbrer",)
    template_name = 'AdmissionApplication/entrance.html'
    form_class = UserEntranceForm
    def post(self, request, *args, **kwargs):
        application_number = self.request.POST.get("application_number")
        s=False
        who=False
        for a in User.objects.values_list("application_number",flat=True ):
            user = get_object_or_404(User, application_number=a)  
            pk=user.pk 
            #他に誰か入っている人がいるか
            if user.achivement_entrance and user.achivement_exit is None and not int(application_number)==int(a):
                who=True
                print(who)
            #入力された入館申請番号があるか
            if int(a)==int(application_number):
                s=True     
        if s==True :
            user = get_object_or_404(User, application_number=application_number)
            entrance_time=user.entrance_schedule
            exit_time=user.exit_schedule
            approval=user.approval
            time=timezone.now()
            if user.achivement_entrance and user.achivement_exit:
                messages.info(self.request, '既に入退館済みです.')
                return HttpResponseRedirect(reverse('entrance'))
            elif approval==True and time>entrance_time and time>exit_time and user.achivement_entrance==None:
                messages.info(self.request, '入館申請出来る時間が過ぎています.')
                return HttpResponseRedirect(reverse('entrance'))
            elif who==True and approval==True and time>entrance_time :
                messages.info(self.request, '現在まだ入っている方がいらっしゃいます.')
                return HttpResponseRedirect(reverse('entrance'))
            elif approval==True and time>entrance_time:
                user = get_object_or_404(User, application_number=application_number)  
                pk=user.pk 
                return HttpResponseRedirect(reverse('entrancewithID', kwargs={'pk':pk}))
            elif approval==True :
                messages.info(self.request, '入館申請出来る時間ではありません.')
                return HttpResponseRedirect(reverse('entrance'))
            else :
                messages.info(self.request, '承認されていません.')
                return HttpResponseRedirect(reverse('entrance'))
        else :
            messages.info(self.request, '入館申請番号が間違っています.')
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

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        return HttpResponseRedirect(reverse('list'))

def UserStatusChange(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        if user.approval == False :
            user.approval = True
            
        template = get_template('AdmissionApplication/mail/create_approval_mail.html')
        mail_ctx={
            'user_name': user.user_name,
            'entrance_schedule': user.entrance_schedule,
            'exit_schedule': user.exit_schedule,
               }
        EmailMessage(
            subject='データセンター入館申請結果のお知らせ',
            body=template.render(mail_ctx),
            to=[user.mail_address],
    #           cc=[],
               bcc=['t17cs049@gmail.com'],
        ).send() 
    user.save()
    
    return redirect('list')

def UserRejejctChange(request, pk):
    user = get_object_or_404(User, pk=pk)

    template = get_template('AdmissionApplication/mail/create_reject_mail.html')
    mail_ctx={
       'user_name': user.user_name,
            }
    EmailMessage(
        subject='データセンター入館申請結果のお知らせ',
        body=template.render(mail_ctx),
        to=[user.mail_address],
    #           cc=[],
            bcc=['t17cs049@gmail.com'],
    ).send() 
            
    user.delete()       
    return redirect('list')

