from django.urls import path
from .views import UserAddView, MenuView

appname='admissionapplication'
urlpatterns = [
    path('main_test/', MenuView, name='menu'),
    path('admission/', UserAddView.as_view(), name='admission'),
    ]