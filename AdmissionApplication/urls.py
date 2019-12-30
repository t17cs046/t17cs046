from django.urls import path
from .views import UserAddView, MenuView, UserList, UserShowWithIDView

appname='admissionapplication'
urlpatterns = [
    path('menu_test/', MenuView, name='menu'),
    path('admission/', UserAddView.as_view(), name='admission'),
    path('user_list', UserList.as_view(), name='list'),
    path('<int:pk>/show', UserShowWithIDView.as_view(), name='showwithID'),
    ]