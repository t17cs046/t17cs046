from django.urls import path
from .views import *

appname='admissionapplication'
urlpatterns = [
    path('menu_test/', MenuView, name='menu'),
    path('admission/', UserAddView.as_view(), name='admission'),
   # path('<int:pk>/result/', ResultView, name='result'),
    ]