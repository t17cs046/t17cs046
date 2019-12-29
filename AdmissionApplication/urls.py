from django.urls import path
from .views import *


appname='admissionapplication'
urlpatterns = [
    path('menu_test/', MenuView, name='menu'),
    path('admission/', UserAddView.as_view(), name='admission'),
    path('result/<int:id>/<メールアドレス>/<申請番号>/', ResultView, name='result'),
    path('user_list', UserList.as_view(), name='list'),

    ]