from django.urls import path
from django.contrib.auth import views as auth_views

from . import views # import views so we can use them in urls.

app_name = 'QuitSoonApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('today/', views.today, name='today'),
    path('paquets/', views.paquets, name='paquets'),
    path('alternatives/', views.alternatives, name='alternatives'),
    path('suivi/', views.suivi, name='suivi'),
    path('objectifs/', views.objectifs, name='objectifs'),
    path('profile/', views.profile, name='profile'),
]
