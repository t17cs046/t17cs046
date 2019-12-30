from django import forms
from .models import User

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["user_name", "organization_name", "phone_number", "mail_address", "entrance_schedule", "exit_schedule", "purpose_of_admission"]
        
        
class UserApproval(forms.Form): 
    status = (
        (0, 'not yet'),
        (1, 'yet'),
        (2, 'block')
        )
    user_id = forms.IntegerField(label='ID')
    approval = forms.ChoiceField(label='APPROVAL',widget=forms.Select, choices=status)
    
class UserIdForm(forms.Form):
    user_id = forms.IntegerField(label='ID')    