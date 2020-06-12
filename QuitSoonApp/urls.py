from django.urls import path
from django.contrib.auth import views as auth_views

from . import views # import views so we can use them in urls.
from QuitSoonApp.dash_apps import smoke_app

app_name = 'QuitSoonApp'

urlpatterns = [
    path('', views.index, name='index'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),

    path('today/', views.today, name='today'),
    path('suivi/', views.suivi, name='suivi'),
    path('objectifs/', views.objectifs, name='objectifs'),

    path('paquets/', views.paquets, name='paquets'),
    path('delete_pack/<id_pack>/',
        views.delete_pack,
        name='delete_pack'),
    path('change_g_per_cig/', views.change_g_per_cig, name='change_g_per_cig'),
    path('smoke/', views.smoke, name='smoke'),
    path('delete_smoke/<id_smoke>/', views.delete_smoke, name='delete_smoke'),
    path('smoke_list/', views.smoke_list, name='smoke_list'),

    path('alternatives/', views.alternatives, name='alternatives'),
    path('delete_alternative/<id_alternative>/',
        views.delete_alternative,
        name='delete_alternative'),
    path('health/', views.health, name='health'),
    path('su_ecig/', views.su_ecig, name='su_ecig'),
    path('delete_health/<id_health>/', views.delete_health, name='delete_health'),

    path('profile/', views.profile, name='profile'),
    path('new_name/', views.new_name, name='new_name'),
    path('new_email/', views.new_email, name='new_email'),
    path('new_password/', views.new_password, name='new_password'),
    path('new_parameters/', views.new_parameters, name='new_parameters'),

]
