#!/usr/bin/env python

from datetime import date
from decimal import Decimal

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
from .forms import (
    RegistrationForm,
    ParametersForm,
    PaquetFormCreation,
    PaquetFormCustomGInCig,
    TypeAlternativeForm,
    ActivityForm,
    SubstitutForm,
    SmokeForm,
    )
from .modules import ResetProfile, SavePack, SaveSmoke, SaveAlternative

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
    form = PaquetFormCreation(request.user)
    if request.method == 'POST':
        # receive smoking habits from user in a
        form = PaquetFormCreation(request.user, request.POST)
        if form.is_valid():
            new_pack = SavePack(request.user, form.cleaned_data)
            new_pack.create_pack()
            form = PaquetFormCreation(request.user)
    # select users packs for display in paquets page
    paquets = Paquet.objects.filter(user=request.user, display=True)
    context = {
        'form':form,
        # get packs per type
        'ind':paquets.filter(type_cig='IND'),
        'rol':paquets.filter(type_cig='ROL'),
        'cigares':paquets.filter(type_cig='CIGARES'),
        'pipe':paquets.filter(type_cig='PIPE'),
        'nb':paquets.filter(type_cig='NB'),
        'gr':paquets.filter(type_cig='GR'),
        }
    return render(request, 'QuitSoonApp/paquets.html', context)

def delete_pack(request, type_cig, brand, qt_paquet, price):
    """
    Used when user click on the trash of one of the paquet
    Don't delete it but change display attribute into False if already used
    """
    datas = {
        'type_cig':type_cig,
        'brand':brand,
        'qt_paquet':int(qt_paquet),
        'price':Decimal(price.replace(',','.')),
    }
    new_pack = SavePack(request.user, datas)
    new_pack.delete_pack()
    return redirect('QuitSoonApp:paquets')

def change_g_per_cig(request):
    """
    User can change the number of gr per cigarette
    and so chane the price of each cigarette
    """
    if request.method == 'POST':
        form = PaquetFormCustomGInCig(request.user, request.POST)
        if form.is_valid():
            change_pack = SavePack(request.user, form.cleaned_data)
            change_pack.update_pack_g_per_cig()
        else:
            print(form.errors.as_data())
    return redirect('QuitSoonApp:paquets')


def bad(request):
    """User smokes"""
    # check if packs are in parameters to fill fields with actual packs
    packs = Paquet.objects.filter(user=request.user, display=True)
    context = {'packs':packs}
    if packs :
        form = SmokeForm(request.user)
        if request.method == 'POST':
            form = SmokeForm(request.user, request.POST)
            if form.is_valid():
                print(form.cleaned_data)
                smoke = SaveSmoke(request.user, form.cleaned_data)
                smoke.create_conso_cig()
                form = SmokeForm(request.user)
        context['form'] = form
    smoke = ConsoCig.objects.filter(user=request.user)
    context['smoke'] = smoke
    return render(request, 'QuitSoonApp/bad.html', context)

def delete_smoke(request, id_smoke):
    data = {'id_smoke':id_smoke}
    smoke = SaveSmoke(request.user, data)
    smoke.delete_conso_cig()
    return redirect('QuitSoonApp:bad')

def delete_alternative(request, id_smoke):
    """
    Used when user click on the trash of one of the alternative
    Don't delete it but change display attribute into False if already used in ConsoAlternative
    """
    data = {'id_smoke':id_smoke}
    smoke = SaveSmoke(request.user, data)
    smoke.delete_conso_cig()
    return redirect('QuitSoonApp:bad')

def alternatives(request):
    """Healthy parameters, user different activities or substitutes"""
    alternative_form = TypeAlternativeForm(request.user)
    activity_form = ActivityForm(request.user)
    substitut_form = SubstitutForm(request.user)

    if request.method == 'POST':
        # rget wich type of alternative
        form_data = {'type_alternative':request.POST['type_alternative']}
        alternative_form = TypeAlternativeForm(request.user, form_data)
        if alternative_form.is_valid():
            final_data = {'type_alternative': alternative_form.cleaned_data['type_alternative']}

            if alternative_form.cleaned_data['type_alternative']== 'Ac' :
                form_data = {'type_activity':request.POST['type_activity'],
                             'activity':request.POST['activity']}
                activity_form = ActivityForm(request.user, form_data)
                if activity_form.is_valid():
                    # keep only fields from alternative_form & activity_form
                    final_data['type_activity'] = activity_form.cleaned_data['type_activity']
                    final_data['activity'] = activity_form.cleaned_data['activity']
                    # Create a SaveAlternative object and create a new alternative
                    new_alternative = SaveAlternative(request.user, final_data)
                    new_alternative.create_alternative()

                    alternative_form = TypeAlternativeForm(request.user)
                    activity_form = ActivityForm(request.user)
                    substitut_form = SubstitutForm(request.user)

            elif alternative_form.cleaned_data['type_alternative'] == 'Su' :
                form_data = {'substitut':request.POST['substitut'],
                             'nicotine':request.POST['nicotine']}
                substitut_form = SubstitutForm(request.user, form_data)
                if substitut_form.is_valid():
                    # keep only fields from alternative_form & substitut_form
                    final_data['substitut'] = substitut_form.cleaned_data['substitut']
                    final_data['nicotine'] = substitut_form.cleaned_data['nicotine']
                    # Create a SaveAlternative object and create a new alternative
                    new_alternative = SaveAlternative(request.user, final_data)
                    new_alternative.create_alternative()

                    alternative_form = TypeAlternativeForm(request.user)
                    activity_form = ActivityForm(request.user)
                    substitut_form = SubstitutForm(request.user)

    # select users packs for display in paquets page
    alternatives = Alternative.objects.filter(user=request.user, display=True)
    context = {
        'alternative_form':alternative_form,
        'activity_form':activity_form,
        'substitut_form':substitut_form,
        # get packs per type
        'Sp':alternatives.filter(type_activity='Sp'),
        'Lo':alternatives.filter(type_activity='Lo'),
        'So':alternatives.filter(type_activity='So'),
        'Su':alternatives.filter(type_alternative='Su'),
        }
    return render(request, 'QuitSoonApp/alternatives.html', context)

def delete_alternative(request, type_alternative, type_activity, activity, substitut, nicotine):
    """
    Used when user click on the trash of one of the alternative
    Don't delete it but change display attribute into False if already used in ConsoAlternative
    """
    data = {
        'type_alternative':type_alternative,
        'type_activity':type_activity,
        'activity':activity,
        'substitut':substitut,
        'nicotine':nicotine,
    }
    new_alternative = SaveAlternative(request.user, data)
    new_alternative.delete_alternative()
    return redirect('QuitSoonApp:alternatives')


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
