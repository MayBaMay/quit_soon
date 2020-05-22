from django.urls import path
from django.contrib.auth import views as auth_views

from . import views # import views so we can use them in urls.

app_name = 'QuitSoonApp'

urlpatterns = [
    path('', views.index, name='index'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),

    path('today/', views.today, name='today'),
    path('suivi/', views.suivi, name='suivi'),
    path('objectifs/', views.objectifs, name='objectifs'),

    path('paquets/', views.paquets, name='paquets'),
    path('delete_pack/<type_cig>/<brand>/<qt_paquet>/<price>/',
        views.delete_pack,
        name='delete_pack'),
    path('change_g_per_cig/', views.change_g_per_cig, name='change_g_per_cig'),
    path('bad/', views.bad, name='bad'),
    path('bad_history/', views.bad_history, name='bad_history'),

    path('alternatives/', views.alternatives, name='alternatives'),
    path('delete_alternative/<type_alternative>/<type_activity>/<activity>/<substitut>/<nicotine>/',
        views.delete_alternative,
        name='delete_alternative'),
    path('good/', views.good, name='good'),
    path('good_history/', views.good_history, name='good_history'),

    path('profile/', views.profile, name='profile'),
    path('new_name/', views.new_name, name='new_name'),
    path('new_email/', views.new_email, name='new_email'),
    path('new_password/', views.new_password, name='new_password'),
    path('new_parameters/', views.new_parameters, name='new_parameters'),

]
