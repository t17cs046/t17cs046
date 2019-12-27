from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView,UpdateView
from .models import User
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from .forms import UserEntranceLogin,UserForm
from django.utils import timezone
from django.db import models

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
    #fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number",)
    template_name = 'AdmissionApplication/entrance.html'
    def post(self, request, *args, **kwargs):
        print(self);
        print(request);
        print(*args);
        application_number = self.request.POST.get('application_number')
        #post = get_object_or_404(User, pk=application_number)
        #user = User.objects.get(User,pk=application_number)
        #user = get_object_or_404(User, pk=application_number)
        #context = super().get_context_data(**kwargs)
        #context['form'] = UserEntranceLogin()
        #context['user'] = user
        #user_name=self.request.POST.get('user_name')
        #organization_name=self.request.POST.get('organaization_name')
        #phone_number=self.request.POST.get('phone_number')
        #mail_adress=self.request.POST.get('mail_adress')
        #entrance_shedule=self.request.POST.get('entrance_shedule')
        #exit_shedule=self.request.POST.get('exit_shedule')
        #purpose_of_admission=self.request.POST.get('purpose_of_admission')
        #user = get_object_or_404(User, pk=application_number)
        #user.user_name=user_name
        #user.organization_name=organization_name
        #user.phone_number=phone_number
        #user.mail_adress=mail_adress
        #user.entrance_shedule=entrance_shedule
        #user.exit_shedule=exit_shedule
        #user.purpose_of_admission=purpose_of_admission
        #user.save()
        
        if User.objects.all().filter(pk=application_number) :
            return HttpResponseRedirect(reverse('entrancewithID', args=(application_number,)))
        else :
            return HttpResponseRedirect(reverse('entrance'))
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserEntranceLogin()
        print(context);
        return context    

class UserEntranceWithIDView(UpdateView):
    model = User
    fields = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number")
    template_name = 'AdmissionApplication/entrancewithID.html'
    def post(self, request, *args, **kwargs):
        application_number = self.request.POST.get('application_number')
        user = get_object_or_404(User, pk=application_number)
        user.save()
        return HttpResponseRedirect(reverse('list'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserEntranceLogin(initial = {'application_number' : self.kwargs.get('pk')})
        return context    


'''
    def form_valid(self, form):
        ctx = {'form': form}
        if self.request.POST.get('next', '') == 'entrance':
            user_id = self.request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            user.achivement_entrance = models.DateTimeField(default=timezone.now)
            user.save()
            return render(self.request, 'AdmissionApplication/menu.html', ctx)
        if self.request.POST.get('next', '') == 'back':      
            #user_id = self.request.POST.get('application_number')
            #achivement_entrance=self.request.POST.get('achivement_entrance')
            user = get_object_or_404(User, pk=user_id)
            user.achivement_entrance = models.DateTimeField(default=timezone.now)
            print(user.achivement_entrance+"iiiiiiii");
            user.save()
            return render(self.request, 'AdmissionApplication/menu.html', ctx)
        if self.request.POST.get('next', '') == 'create':
            return super().form_valid(form)
        
'''    
'''           
class UserEntranceBotton(TemplateView):    
    model=User
    fids = ("user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission","application_number")
    template_name = 'AdmissionApplication/entrance.html'
    def pelost(self, request, *args, **kwargs):
        application_number = self.request.POST.get('application_number')
        user = User.objects.get(pk=application_number)
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserEntranceLogin()
        context['user'] = user
        return self.render_to_response(context)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserEntranceLogin(initial = {'application_number' : self.kwargs.get('pk')})
        return context
    def get_success_url(self):
        print(self.object.id);
        return reverse('admissionapplication:entrance', kwargs={'pk': self.object.id})
'''    