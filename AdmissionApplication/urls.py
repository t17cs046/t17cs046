from django.urls import path
from .views import *

appname='admissionapplication'
urlpatterns = [
    path('menu_test/', MenuView, name='menu'),
    path('admission/', UserAddView.as_view(), name='admission'),
    path('result/<メールアドレス>/<申請番号>/', ResultView, name='result'),
    
    path('user_list', UserList.as_view(), name='list'),
    path('<int:pk>/show', UserShowWithIDView.as_view(), name='showwithID'),
    path('<int:pk>/userstatusChange', UserStatusChange, name='UserStatusChange'),
    path('<int:pk>/userrejectChange', UserRejejctChange, name='UserRejectChange'),
    
    path('entrance',UserEntrance.as_view(),name='entrance'),
    path('<int:pk>/entrance',UserEntranceWithIDView.as_view(),name='entrancewithID'),
    
    path('schedule', UserScheduleList.as_view(), name='schedulelist'),

    ]