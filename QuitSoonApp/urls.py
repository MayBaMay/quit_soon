#!/usr/bin/env python

"""App urls"""

from __future__ import unicode_literals
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from QuitSoonApp.forms.registration_forms import EmailValidationOnResetPassword
from . import views

app_name = 'QuitSoonApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('legals/', views.legals, name='legals'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),

    path('today/', views.today, name='today'),
    path('report/', views.report, name='report'),
    path('charts/', TemplateView.as_view(template_name="QuitSoonApp/charts.html"),
                   name='charts'),
    path('api/chart/data', views.ChartData.as_view(), name='ChartApi' ),
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
    path('delete_health/<id_health>/', views.delete_health, name='delete_health'),
    path('health_list/', views.health_list, name='health_list'),

    path('profile/', views.profile, name='profile'),
    path('new_name/', views.new_name, name='new_name'),
    path('new_email/', views.new_email, name='new_email'),
    path('new_password/', views.new_password, name='new_password'),
    path('new_parameters/', views.new_parameters, name='new_parameters'),
    path('delete_account/', views.delete_account, name='delete_account'),

    # Password reset
    #(ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             form_class=EmailValidationOnResetPassword
             ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
             ),
         name='password_reset_done'),

    path('reset/{uidb64}/{token}/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
             ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
             ),
         name='password_reset_complete'),

]
