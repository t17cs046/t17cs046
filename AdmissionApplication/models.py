from django.db import models

# Create your models here.

class User(models.Model):
    user_name = models.CharField(max_length=20)
    organization_name = models.CharField(max_length=20)       
    phone_number = models.CharField(max_length=13)
    mail_address = models.EmailField(('mail address'), unique=True)

    def __str__(self):
        return self.user_name     
       
       
class Entrance_Exit_information(models.Model):
    entrance_schedule = models.DateField(blank=True,null=True)      
    exit_schedule = models.DateField(blank=True,null=True)
    purpose_of_admission = models.CharField(max_length=100) 
    
class Admission_information(models.Model):
    application_date = models.DateField(blank=True,null=True)
    application_number = models.IntegerField(max_length=7)
    password = models.CharField(max_length=8)      
    approval = models.BooleanField(default=False)
    
class Achievement_information(models.Model):
    achivement_entrance = models.DateField(blank=True,null=True)      
    achivement_exit = models.DateField(blank=True,null=True) 

  