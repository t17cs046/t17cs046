from django.urls import path
from .views import UserAddView, MenuView, UserList,UserEntrance#,UserEntranceBotton

appname='admissionapplication'
urlpatterns = [
    path('menu_test/', MenuView, name='menu'),
    path('admission/', UserAddView.as_view(), name='admission'),
    path('user_list', UserList.as_view(), name='list'),
    path('entrance',UserEntrance.as_view(),name='entrance'),
    #path('entrance/<int:question_id>',UserEntranceBotton.as_view(),name='entrance_id')
    ]