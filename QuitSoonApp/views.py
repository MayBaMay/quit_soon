from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.models import User

from .models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)
from .forms import RegistrationForm, LoginForm


def index(request):
    """index View"""
    if request.user.is_authenticated:
        return redirect('QuitSoonApp:today')
    else:
        return render(request, 'index.html')

def register_view(request):
    """Registration view creating a user"""
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('QuitSoonApp:index')
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    """Login view connecting a user"""
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('QuitSoonApp:index')
    return render(request, 'registration/login.html', {'form':form})

def today(request):
    return render(request, 'QuitSoonApp/today.html')

def profile(request):
    return render(request, 'QuitSoonApp/profile.html')

def paquets(request):
    return render(request, 'QuitSoonApp/paquets.html')

def alternatives(request):
    return render(request, 'QuitSoonApp/alternatives.html')

def suivi(request):
    return render(request, 'QuitSoonApp/suivi.html')

def objectifs(request):
    return render(request, 'QuitSoonApp/objectifs.html')
