from django import forms
from .models import User
from pip._vendor.pkg_resources import require
from django.forms.widgets import DateTimeInput

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission"]
        widgets = {
            "entrance_schedule" : DateTimeInput(attrs={'type' : 'datetime-local', 'format': 'yyyy-mm-dd HH:ii'}),
            "exit_schedule" : DateTimeInput(attrs={'type' : 'datetime-local', 'format': 'yyyy-mm-dd HH:ii'}),
            }
        
        
class UserEntranceLogin(forms.Form):
    application_number=forms.IntegerField(label='入館申請番号')
    #application_number=forms.IntegerField(label='入館申請番号',required=True)
class UserEntranceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["application_number",]
            
    
class UserIdForm(forms.Form):
    user_id = forms.IntegerField(label='ID')    
