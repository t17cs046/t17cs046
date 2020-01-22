from django import forms
from .models import User
from pip._vendor.pkg_resources import require
from django.contrib.admin import widgets


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission"]

        
class UserEntranceLogin(forms.Form):
    application_number=forms.IntegerField(label='入館申請番号')
    #application_number=forms.IntegerField(label='入館申請番号',required=True)
class UserEntranceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["application_number",]
class UserChangeDeleteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["application_number","password"]
                       
class UserPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["password"]
        widgets={"password":forms.PasswordInput()}
    
class UserIdForm(forms.Form):
    user_id = forms.IntegerField(label='ID')    
