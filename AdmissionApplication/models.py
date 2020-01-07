from django.db import models
from django.utils import timezone
from django.urls import reverse
# Create your models here.

class User(models.Model):
    #氏名
    user_name = models.CharField('氏名',max_length=20)
    #組織名
    organization_name = models.CharField('組織名',max_length=20)       
    #電話番号
    phone_number = models.CharField('電話番号',max_length=13)
    #メールアドレス
    mail_address = models.CharField('メールアドレス',max_length=255)
    #入館予定
    entrance_schedule = models.DateTimeField('入館予定日時',blank=False,null=False)
    #entrance_schedule = models.DateTimeField('入館予定日時',blank=True,null=True)      
    #退館予定
    exit_schedule = models.DateTimeField('退館予定日時',blank=False,null=False)
    #exit_schedule = models.DateTimeField('退館予定日時',blank=True,null=True)

    #入館目的
    purpose_of_admission = models.CharField('入館目的',max_length=100) 
    #申請時間
    application_date = models.DateTimeField('申請時間',default=timezone.now, blank=True,null=True)
    
    #入館申請番号
    application_number = models.PositiveIntegerField('入館申請番号',default=0)
    #application_number = models.PositiveIntegerField('入館申請番号',default=0,primary_key=True)
    #ワンタイムパスワード
    password = models.CharField('パスワード',max_length=8, null=True)      
    #承認可否
    approval = models.BooleanField('承認可否',default=False)
    #入館実績
    achivement_entrance = models.DateTimeField('入館実績日時',blank=True,null=True)      
    #退館実績
    achivement_exit = models.DateTimeField('退館実績日時',blank=True,null=True) 

    def __str__(self):
        return self.user_name   
      
    def get_absolute_url(self):
        return reverse("result", kwargs={
            'id': self.pk,
            'メールアドレス': self.mail_address,
            '申請番号': self.application_number
            })
