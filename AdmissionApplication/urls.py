from django.urls import path
from .views import *

appname='admissionapplication'
urlpatterns = [
    path('menu_test/', MenuView, name='menu'),
    path('admission/', UserAddView.as_view(), name='admission'),
    path('result/<メールアドレス>/<申請番号>/', ResultView, name='result'),
    
    path('user_list', UserList.as_view(), name='list'),
    path('<int:pk>/show', UserShowWithIDView.as_view(), name='showwithID'),
    
    path('entrance',UserEntrance.as_view(),name='entrance'),
    path('<int:pk>/entrance',UserEntranceWithIDView.as_view(),name='entrancewithID'),

    path('changedelete',UserChangeDeleteView.as_view(),name='changedelete'),
    path('<int:pk>/change',UserChangeWithIDView.as_view(),name='changewithID'),
    path('<int:pk>/changedeleteshow',UserChangeDeleteShowWithIDView.as_view(),name='changedeleteshowwithID'),
    path('<int:pk>/delete',UserDeleteWithIDView.as_view(),name='deletewithID'),
    ]