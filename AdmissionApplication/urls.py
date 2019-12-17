from django.urls import path
from .views import UserAddView

appname='admissionapplication'
urlpatterns = [
    path('admission/', UserAddView.as_view(), name='admission'),
    ]