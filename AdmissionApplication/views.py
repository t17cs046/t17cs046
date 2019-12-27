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
    success_url = '../menu_test'
    def form_valid(self, form):
        print(self.request.POST.get('next', '') +"aaaaaaaaaaaaaaaaaaaaaaaaaaa");
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
            form.achivement_entrance = models.DateTimeField(default=timezone.now)
            print(user.achivement_entrance+"iiiiiiii");
            form.save()
            return super().form_valid(form)
            #return render(self.request, 'AdmissionApplication/menu.html', ctx)
        if self.request.POST.get('next', '') == 'create':
            return super().form_valid(form)
        
    def post(self, request, *args, **kwargs):
        print(self);
        print(request);
        print(*args);
        #print(application_number);
        application_number = self.request.POST.get('application_number')
        print(application_number);
        #if User.application_number==application_number:
        user = User.objects.get(pk=application_number)
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserEntranceLogin()
        context['user'] = user
        return self.render_to_response(context)
        #else:
            #context = super().get_context_data(**kwargs) 
            #return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_id'] = UserEntranceLogin()
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