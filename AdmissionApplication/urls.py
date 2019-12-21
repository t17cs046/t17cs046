from django.urls import path
from .views import UserAddView, MenuView, UserList

appname='admissionapplication'
urlpatterns = [
    path('menu_test/', MenuView, name='menu'),
    path('admission/', UserAddView.as_view(), name='admission'),
    path('user_list', UserList.as_view(), name='list'),
    ]