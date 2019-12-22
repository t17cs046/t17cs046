from django.db import models
from django.utils import timezone

# Create your models here.

class User(models.Model):
    #氏名
    user_name = models.CharField(max_length=20)
    #組織名
    organization_name = models.CharField(max_length=20)       
    #電話番号
    phone_number = models.CharField(max_length=13)
    #メールアドレス
    mail_address = models.CharField(max_length=255)
    #入館予定
    entrance_schedule = models.DateTimeField(blank=True,null=True)      
    #退館予定
    exit_schedule = models.DateTimeField(blank=True,null=True)
    #入館目的
    purpose_of_admission = models.CharField(max_length=100) 
    #申請時間
    application_date = models.DateTimeField(default=timezone.now, blank=True,null=True)
    
    #入館申請番号
    application_number = models.PositiveIntegerField(default=0)
    #ワンタイムパスワード
    password = models.CharField(max_length=8)      
    #承認可否
    approval = models.BooleanField(default=False)
    #入館実績
    achivement_entrance = models.DateTimeField(blank=True,null=True)      
    #退館実績
    achivement_exit = models.DateTimeField(blank=True,null=True) 

    def __str__(self):
        return self.user_name     
      
