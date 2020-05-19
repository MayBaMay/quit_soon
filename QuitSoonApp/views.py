from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.models import User

from .models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
    Objectif, Trophee
)
from .forms import RegistrationForm, ParametersForm, PaquetForm
from .modules.resetprofile import ResetProfile
from .modules.save_pack import SavePack

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
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('QuitSoonApp:index')
    return render(request, 'registration/login.html', {'form':form})

def today(request):
    """Welcome page if user.is_authenticated. Actions for the day"""
    return render(request, 'QuitSoonApp/today.html')

def profile(request):
    """User profile page with authentication infos and smoking habits"""
    context = {'userprofile':None}
    if request.user.is_authenticated:
        userprofile = UserProfile.objects.filter(user=request.user)
        if userprofile:
            userprofile = UserProfile.objects.get(user=request.user)
        else:
            userprofile = 'undefined'
        context = { 'userprofile':userprofile}
    return render(request, 'QuitSoonApp/profile.html', context)

def new_name(request):
    """View changing user name"""
    response_data = {}
    user = request.user
    if request.method == 'POST':
        new_name_user = request.POST['username']
        if User.objects.filter(username=new_name_user).exists():
            response_data = {'response':"name already in db", 'name':user.username}
        else:
            user.username = new_name_user
            user.save()
            if user.username == new_name_user:
                response_data = {'response':"success", 'name':user.username}
            else:
                response_data = {'response':"fail", 'name':user.username}
    else:
        raise Http404()
    return HttpResponse(JsonResponse(response_data))

def new_email(request):
    """View changing user email"""
    response_data = {}
    user = request.user
    if request.method == 'POST':
        new_email_user = request.POST['email']
        if User.objects.filter(email=new_email_user).exists():
            response_data = {'response':"email already in DB"}
        else:
            user.email = new_email_user
            user.save()
            if user.email == new_email_user:
                response_data = {'response':"success"}
            else:
                response_data = {'response':"fail"}
    else:
        raise Http404()
    return HttpResponse(JsonResponse(response_data))

def new_password(request):
    """View changing user password"""
    response_data = {}
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            response_data = {'response':"success"}
        else:
            old_password = request.POST['old_password']
            new_password1 = request.POST['new_password1']
            new_password2 = request.POST['new_password2']
            if request.user.check_password(old_password) == False:
                response_data = {'response':"incorrect old password"}
            elif new_password1 != new_password2:
                response_data = {'response':"new password not confirmed"}
            else:
                response_data = {'response':"incorrect newpassword"}
    else:
        raise Http404()
    return HttpResponse(JsonResponse(response_data))

def new_parameters(request):
    """View changing user smoking habits when starting using app"""
    response_data = {'response':None}
    if request.method == 'POST':
        form = ParametersForm(request.POST)
        if form.is_valid():
            reset = ResetProfile(request.user, request.POST)
            userprofile = reset.new_profile()
            response_data = {'response':'success'}
    else:
        raise Http404()
    return HttpResponse(JsonResponse(response_data))

def paquets(request):
    """Smoking parameters, user different packs"""
    form = PaquetForm(request.user)
    if request.method == 'POST':
        # receive smoking habits from user in a
        form = PaquetForm(request.user, request.POST)
        if form.is_valid():
            new_pack = SavePack(request.user, form.cleaned_data)
            new_pack.create_pack()
            form = PaquetForm(request.user)
    # select users packs for display in paquets page
    paquets = Paquet.objects.filter(user=request.user, display=True)
    context = {
        'form':form,
        # get packs per type
        'ind':paquets.filter(type_cig='IND'),
        'rol':paquets.filter(type_cig='ROL'),
        'cigares':paquets.filter(type_cig='CIGARES'),
        'cigarios':paquets.filter(type_cig='CIGARIOS'),
        'pipe':paquets.filter(type_cig='PIPE'),
        'nb':paquets.filter(type_cig='NB'),
        'gr':paquets.filter(type_cig='GR'),
        }
    return render(request, 'QuitSoonApp/paquets.html', context)

def delete_pack(request):
    """
    Used when user click on the trash of one of the paquet
    Don't delete it but change display attribute into False if already used
    """
    pass


def bad(request):
    """User smokes"""
    return render(request, 'QuitSoonApp/bad.html')

def bad_history(request):
    """User smoking history page"""
    return render(request, 'QuitSoonApp/bad_history.html')

def alternatives(request):
    """Healthy parameters, user different activities or substitutes"""
    return render(request, 'QuitSoonApp/alternatives.html')

def good(request):
    """User do a healthy activity or uses substitutes"""
    return render(request, 'QuitSoonApp/good.html')

def good_history(request):
    """User healthy history page"""
    return render(request, 'QuitSoonApp/good_history.html')

def suivi(request):
    """Page with user results, graphs..."""
    return render(request, 'QuitSoonApp/suivi.html')

def objectifs(request):
    """Page with user trophees and goals"""
    return render(request, 'QuitSoonApp/objectifs.html')
