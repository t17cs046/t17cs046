from django.db import models

# Create your models here.

class User(models.Model):
    user_name = models.CharField(max_length=20)
    organization_name = models.CharField(max_length=20)       
    phone_number = models.CharField(max_length=13)
    mail_address = models.CharField(max_length=10)
    entrance_schedule = models.DateField(blank=True,null=True)      
    exit_schedule = models.DateField(blank=True,null=True)
    purpose_of_admission = models.CharField(max_length=100) 
    application_date = models.DateField(blank=True,null=True)
    application_number = models.IntegerField()
    password = models.CharField(max_length=8)      
    approval = models.BooleanField(default=False)
    achivement_entrance = models.DateField(blank=True,null=True)      
    achivement_exit = models.DateField(blank=True,null=True) 

    def __str__(self):
        return self.user_name     
      
"""       
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

class Infomation(models.Model):
    user = models.ForeignKey(User, blank=True,null=True,verbose_name='user', on_delete=models.PROTECT)
    entrance_exit_information = models.ForeignKey(Entrance_Exit_information, blank=True,null=True,verbose_name='entrance_exit_information', on_delete=models.PROTECT)
    admission_information = models.ForeignKey(Admission_information, blank=True,null=True,verbose_name='admission_information', on_delete=models.PROTECT)
    achivement_information = models.ForeignKey(Achievement_information, blank=True,null=True,verbose_name='achivement_information', on_delete=models.PROTECT)
"""