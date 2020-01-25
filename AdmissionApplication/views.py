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
from datetime import date, datetime
from django.db import models
from Team5.wsgi import application
from django.contrib.admin.utils import lookup_field
from unicodedata import lookup
from django.contrib import messages
from django.db.models import Q
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
            random_number=random.randrange(999) + int(datetime.now().strftime('%y')) * 100000 + int(datetime.now().strftime('%m')) * 1000
            while(User.objects.filter(application_number__exact=random_number).count() > 0):
                random_number = random.randrange(999) + int(datetime.now().strftime('%y')) * 100000 + int(datetime.now().strftime('%m')) * 1000
            user.application_number = random_number
            user.password = ''.join([random.choice(word) for i in range(8)])
            
        if self.request.POST.get('next', '') == 'confirm':
            form_user_name = self.request.POST.get("user_name")
            form_organization_name = self.request.POST.get("organization_name")
            form_phone_number = self.request.POST.get("phone_number")
            form_mail_address  = self.request.POST.get("mail_address")
            form_entrance_schedule = self.request.POST.get("entrance_schedule")
            form_exit_schedule = self.request.POST.get("exit_schedule")
            phone_serch = re.search(phone_regex, form_phone_number)
            check = True
            #承認済み利用者を取得
            all_entries = User.objects.filter(approval__exact="True")
            #氏名と異なる利用者を取得
            all_entries = all_entries.exclude(user_name=form_user_name)
            #組織名と異なる利用者を取得
            all_entries = all_entries.exclude(organization_name=form_organization_name)
            #自分の入館時間<他の利用者の退館時間<自分の退館時間
            
            overlapping_1 = all_entries.filter(exit_schedule__range=(form_entrance_schedule, form_exit_schedule))
            #自分の入館時間<他の利用者の入館時間<自分の退館時間
            overlapping_2 = all_entries.filter(entrance_schedule__range=(form_entrance_schedule, form_exit_schedule))
            #他の利用者の入館時間<自分の入館時間<自分の退館時間<他の利用者の退館時間
            overlapping_3 = all_entries.filter(entrance_schedule__lt=form_entrance_schedule)
            overlapping_3 = overlapping_3.filter(exit_schedule__gt=form_exit_schedule)

            today = datetime.now().strftime('%Y-%m-%d %H:%M')
           
            if (re.match('[ｦ-ﾟ]', form_user_name) != None):
                messages.error(self.request, '氏名に半角カナは使用できません.')
                check = False
            if 'None' in str(phone_serch):
                messages.error(self.request, '有効な電話番号を入力してください．')
                check = False           
            if (re.match('[A-Za-z0-9\._+]+@[A-Za-z]+\.[A-Za-z]', form_mail_address) == None) :
                messages.error(self.request, '有効なメールアドレスを入力してください.')
                check = False      
            if form_entrance_schedule > form_exit_schedule:
                messages.error(self.request, '入館予定日時が退館予定日時より前になっています．')
                check = False
            if form_entrance_schedule < today:
                messages.error(self.request, '入館予定日時が現在時刻より前になっています.')
                check = False
            if overlapping_1.count() > 0 or overlapping_2.count() > 0 or overlapping_3.count() > 0:
                messages.error(self.request, '他の利用者の方と予定日時が重複しています.')
                check = False
            if check:
                return render(self.request, 'AdmissionApplication/confirm.html', ctx)
            else:
                return render(self.request, 'AdmissionApplication/admission.html', ctx)
            
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
        return HttpResponseRedirect(reverse('list')).order_by('-entrance_schedule')
    
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
        user_list=User.objects.filter(application_number__exact=self.request.POST.get("application_number"))
        print(user_list)
        if(user_list.count() > 0):   
            user = get_object_or_404(User, application_number=application_number)  
            pk=user.pk  
            if(user.password ==password):
                return HttpResponseRedirect(reverse('changedeleteshowwithID', kwargs={'pk':pk}))
            else: 
                messages.error(self.request,'パスワードが間違っています.')
        else:
            messages.error(self.request, '入館申請番号が間違っています')
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
            ''' 
        elif self.request.POST.get('next', '') == 'back':
            return HttpResponseRedirect(reverse('changedelete')) '''
        
        else :
            return HttpResponseRedirect(reverse('changedeleteshowwidhID'))


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
    #           bcc=[],
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
    #        bcc=[],
    ).send() 
            
    user.delete()       
    return redirect('list')

class UserChangeWithIDView(UpdateView):
    model = User
    #fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number")
    template_name = 'AdmissionApplication/changewithID.html'
    form_class = ApplicationForm
    success_url = '../edit_result'
    
    def post(self,request, *args, **kwargs):
        if self.request.POST.get('next', '') == 'change':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            name = self.request.POST.get('user_name')
            organization_name=self.request.POST.get('organization_name')
            phone_number = self.request.POST.get('phone_number')
            mail_address = self.request.POST.get('mail_address')
            entrance_schedule = self.request.POST.get('entrance_schedule')
            exit_schedule = self.request.POST.get('exit_schedule')
            purpose_of_admission = self.request.POST.get('purpose_of_admission')
            password = self.request.POST.get('password')
            user.user_name=name
            user.organization_name = organization_name
            user.phone_number = phone_number
            user.mail_address = mail_address
            user.entrance_schedule = entrance_schedule
            user.exit_schedule = exit_schedule
            user.purpose_of_admission = purpose_of_admission
            pk=user.pk
            phone_serch = re.search(phone_regex, user.phone_number)
            check = True
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
            today = datetime.now().strftime('%Y-%m-%d %H:%M')
            if(user.approval == True):
                messages.error(self.request,'承認済のため修正できません.')
                check=False
            elif (re.match('[ｦ-ﾟ]', user.user_name) != None):
                messages.error(self.request, '氏名に半角カナは使用できません.')
                check = False
            elif 'None' in str(phone_serch):
                messages.error(self.request, '有効な電話番号を入力してください．')
                check = False           
            elif (re.match('[A-Za-z0-9\._+]+@[A-Za-z]+\.[A-Za-z]', user.mail_address) == None) :
                messages.error(self.request, '有効なメールアドレスを入力してください.')
                check = False                 
            elif self.request.POST.get("entrance_schedule") > self.request.POST.get("exit_schedule"):
                messages.error(self.request,'入館予定日時が退館予定日時より前になっています.')
                check=False          
            elif self.request.POST.get("entrance_schedule") < today:
                messages.error(self.request,'入館予定日時が現在時刻より前になっています')
                check=False
            elif overlapping_1.count() > 0 or overlapping_2.count() > 0 or overlapping_3.count() > 0:
                messages.error(self.request,'他の利用者と時間が重複しています.')
            elif(user.password != password):
                messages.error(self.request,'パスワードが間違っています.')
                check=False
            if(check==False):
                return HttpResponseRedirect(reverse('changewithID', kwargs={'pk':pk}))    
            template = get_template('AdmissionApplication/mail/change_mail.html')
            mail_ctx={
                'user_name': user.user_name,
                'organization_name': user.organization_name,
                'phone_number': user.phone_number,
                'mail_address': user.mail_address,
                'entrance_schedule': user.entrance_schedule,
                'exit_schedule': user.exit_schedule,
                'purpose_of_admission': user.purpose_of_admission,
                'application_number': user.application_number,
                'password': user.password,
                }
            EmailMessage(
                subject='入館申請情報修正完了',
                body=template.render(mail_ctx),
                to=[user.mail_address],
#                cc=[],
#                bcc=[],
            ).send()
            user.save()
            return HttpResponseRedirect(reverse('edit_result'))
        elif self.request.POST.get('next', '') == 'back':
            application_number = kwargs.get('pk')
            user = get_object_or_404(User, pk=application_number)
            pk=user.pk
            return HttpResponseRedirect(reverse('changedeleteshowwithID',kwargs={'pk':pk}))
        else:
            return HttpResponseRedirect(reverse('changedelete'))

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
        if self.request.POST.get('next', '') == 'delete':
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
                return HttpResponseRedirect(reverse('delete_result'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] =  ApplicationForm(initial = {'user_id' : self.kwargs.get('pk')})
        context['form'] = UserPasswordForm()
        return context   
def EditResultView(request):
    return render(request, 'AdmissionApplication/edit_result.html')
def DeleteResultView(request):
    return render(request, 'AdmissionApplication/delete_result.html')

class UserScheduleList(ListView):
    model = User
    template_name = 'AdmissionApplication/schedule_list.html'
    date = timezone.now()

    def post(self, request, *args, **kwargs):
#       user_id = self.request.POST.get('user_id')
#        user = get_object_or_404(User, pk=user_id)
        users = User.objects.filter(entrance_schedule__year=2020)
        print(users.count())
        for user in users:
            user.save()
        return HttpResponseRedirect(reverse('schedulelist'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_list'] = User.objects.filter(
            Q(entrance_schedule__year=date.today().year,entrance_schedule__month=date.today().month,entrance_schedule__day__gte=date.today().day) | Q(entrance_schedule__year=date.today().year,entrance_schedule__month__gte=date.today().month+1) | Q(entrance_schedule__year__gte=date.today().year+1)
            ).order_by("entrance_schedule")
        return context

    def get_queryset(self):
        schedule = self.request.GET.get('schedule')
        print(schedule)
        if schedule:
            schedule_list = User.objects.filter(entrance_schedule__gte=schedule)
        else:
            schedule_list = None
        return schedule_list 

      