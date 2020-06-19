#!/usr/bin/env python

import datetime
from datetime import time as t
# from datetime import date
from decimal import Decimal
import json

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.models import User

from QuitSoonApp.models import (
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
    ChoosePackFormWithEmptyFields, SmokeForm,
    ChooseAlternativeFormWithEmptyFields, HealthForm,
    )
from .modules import (
    ResetProfile,
    PackManager, SmokeManager,
    AlternativeManager, HealthManager,
    SmokeStats, HealthyStats
    )


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
            return redirect('QuitSoonApp:profile')
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
    context = {
        'userprofile':None,
        'user_packs':None,
        }
    if request.user.is_authenticated:
        parameter_form = ParametersForm(request.user, request.POST)
        paquet_form = PaquetFormCreation(request.user)
        context['parameter_form'] = parameter_form
        context['paquet_form'] = paquet_form
        try:
            userprofile = UserProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            userprofile = None
        try:
            paquet_ref = Paquet.objects.get(user=request.user, first=True)
        except ObjectDoesNotExist:
            paquet_ref = None
            # if nor ref_pack, profile is incomplete
            userprofile = None
        # !!!!!!!!! to do!!!!!!!!!except pb more then one first? should not happened but in case
        if userprofile:
            context['userprofile'] = userprofile
            context['paquet_ref'] = paquet_ref
        packs = Paquet.objects.filter(user=request.user, display=True)
        if packs.exists:
            context['user_packs'] = packs
    return render(request, 'QuitSoonApp/profile.html', context)

def new_parameters(request):
    """View changing user smoking habits when starting using app"""
    response_data = {'response':None}
    if request.user.is_authenticated and request.method == 'POST':
        # make request.POST mutable
        data = dict(request.POST)
        for field in data:
            data[field]=data[field][0]
        # check wich form (existing packs or new pack)
        try:
            if data['id_ref_pack'] == None:
                existing_pack = False
            elif data['id_ref_pack'] == '':
                existing_pack = False
            else:
                existing_pack = True
        except:
            existing_pack = False
        # if new pack, createpack with PaquetFormCreation
        if not existing_pack:
            paquet_form = PaquetFormCreation(request.user, data)
            if paquet_form.is_valid():
                new_pack = PackManager(request.user, paquet_form.cleaned_data)
                # define new_pack as the first pack (ref to use for stats)
                new_pack.init_first()
                # create pack
                new_db_object = new_pack.create_pack()
                # include field ref_pack with new pack id in data for ParametersForm
                data['ref_pack'] = new_db_object.id
        # reset parameters
        parameter_form = ParametersForm(request.user, data)
        if parameter_form.is_valid():
            reset = ResetProfile(request.user, parameter_form.cleaned_data)
            reset.new_profile()
        return redirect('QuitSoonApp:profile')
    else:
        raise Http404()

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

def paquets(request):
    """Smoking parameters, user different packs"""
    context = {'first' : False}
    if request.user.is_authenticated:
        form = PaquetFormCreation(request.user)
        if not Paquet.objects.filter(user=request.user).exists():
            context['first'] = True
        if request.method == 'POST':
            # receive smoking habits from user in a
            form = PaquetFormCreation(request.user, request.POST)
            if form.is_valid():
                new_pack = PackManager(request.user, form.cleaned_data)
                new_pack.create_pack()
                form = PaquetFormCreation(request.user)
                context['first'] = False
        # select users packs for display in paquets page
        paquets = Paquet.objects.filter(user=request.user, display=True)
        context['form'] = form
        # get packs per type
        context['ind'] = paquets.filter(type_cig='IND')
        context['rol'] = paquets.filter(type_cig='ROL')
    return render(request, 'QuitSoonApp/paquets.html', context)

def delete_pack(request, id_pack):
    """
    Used when user click on the trash of one of the paquet
    Don't delete it but change display attribute into False if already used
    """
    if Paquet.objects.filter(user=request.user, id=id_pack).exists():
        data = {'id_pack':id_pack}
        new_pack = PackManager(request.user, data)
        new_pack.delete_pack()
        return redirect('QuitSoonApp:paquets')
    else:
        # asked out of form so not expected request from user
        raise Http404()

def change_g_per_cig(request):
    """
    User can change the number of gr per cigarette
    and so chane the price of each cigarette
    """
    if request.method == 'POST':
        form = PaquetFormCustomGInCig(request.user, request.POST)
        if form.is_valid():
            change_pack = PackManager(request.user, form.cleaned_data)
            change_pack.update_pack_g_per_cig()
    return redirect('QuitSoonApp:paquets')


def smoke(request):
    """User smokes"""
    # check if packs are in parameters to fill fields with actual packs
    packs = Paquet.objects.filter(user=request.user, display=True)
    context = {'packs':packs}
    if packs :
        smoke_form = SmokeForm(request.user)
        if request.method == 'POST':
            smoke_form = SmokeForm(request.user, request.POST)
            if smoke_form.is_valid():
                smoke = SmokeManager(request.user, smoke_form.cleaned_data)
                smoke.create_conso_cig()
                smoke_form = SmokeForm(request.user)
        context['smoke_form'] = smoke_form
    smoke = ConsoCig.objects.filter(user=request.user).order_by('-date_cig', '-time_cig')
    context['smoke'] = smoke
    try:
        context['lastsmoke'] = smoke.latest('date_cig', 'time_cig')
    except ObjectDoesNotExist:
        pass
    return render(request, 'QuitSoonApp/smoke.html', context)

def delete_smoke(request, id_smoke):
    """
    Used when user click on the trash of one of his smocke action
    """
    if ConsoCig.objects.filter(user=request.user, id=id_smoke).exists():
        data = {'id_smoke':id_smoke}
        smoke = SmokeManager(request.user, data)
        smoke.delete_conso_cig()
        return redirect('QuitSoonApp:smoke')
    else:
        raise Http404()

def smoke_list(request):
    """list conso cig"""
    context = {}
    if request.user.is_authenticated:
        packs = Paquet.objects.filter(user=request.user, display=True)
        context['packs'] = packs
        if packs.exists():
            smoke = ConsoCig.objects.filter(user=request.user).order_by('-date_cig', '-time_cig')
            if smoke.exists() :
                smoke_list_form = ChoosePackFormWithEmptyFields(request.user)
                if request.method == 'POST':
                    smoke_list_form = ChoosePackFormWithEmptyFields(request.user, request.POST)
                    if smoke_list_form.is_valid():
                        data = smoke_list_form.cleaned_data
                        if data['type_cig_field'] != 'empty':
                            if data['type_cig_field'] == 'given':
                                smoke = smoke.filter(given=True)
                            else:
                                smoke = smoke.filter(paquet__type_cig=data['type_cig_field'])
                                if data['ind_pack_field'] != 'empty':
                                    pack = Paquet.objects.get(id=int(data['ind_pack_field']))
                                    smoke = smoke.filter(paquet__brand=pack.brand)
                                elif data['rol_pack_field'] != 'empty':
                                    pack = Paquet.objects.get(id=int(data['rol_pack_field']))
                                    smoke = smoke.filter(paquet__brand=pack.brand)
                context['smoke'] = smoke
                context['smoke_list_form'] = smoke_list_form
    return render(request, 'QuitSoonApp/smoke_list.html', context)

def alternatives(request):
    """Healthy parameters, user different activities or substitutes"""
    context = {}
    if request.user.is_authenticated:
        alternative_form = TypeAlternativeForm(request.user)
        activity_form = ActivityForm(request.user)
        substitut_form = SubstitutForm(request.user)

        if request.method == 'POST':
            # get wich type of alternative
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
                        # Create a AlternativeManager object and create a new alternative
                        new_alternative = AlternativeManager(request.user, final_data)
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
                        # Create a AlternativeManager object and create a new alternative
                        new_alternative = AlternativeManager(request.user, final_data)
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

def delete_alternative(request, id_alternative):
    """
    Used when user click on the trash of one of the alternative
    Don't delete it but change display attribute into False if already used in ConsoAlternative
    """
    if Alternative.objects.filter(user=request.user, id=id_alternative).exists():
        data = {'id_alternative': id_alternative}
        new_alternative = AlternativeManager(request.user, data)
        new_alternative.delete_alternative()
        return redirect('QuitSoonApp:alternatives')
    else:
        raise Http404()

def health(request):
    """User do a healthy activity or uses substitutes"""
    context = {}
    if request.user.is_authenticated:
        # check if packs are in parameters to fill fields with actual packs
        alternatives = Alternative.objects.filter(user=request.user, display=True)
        context['alternatives'] = alternatives
        if alternatives :
            form = HealthForm(request.user)
            if request.method == 'POST':
                form = HealthForm(request.user, request.POST)
                if form.is_valid():
                    new_health = HealthManager(request.user, form.cleaned_data)
                    new_health.create_conso_alternative()
                    form = HealthForm(request.user)
            context['form'] = form
        health = ConsoAlternative.objects.filter(user=request.user).order_by('-date_alter', '-time_alter')
        context['health'] = health
        try:
            context['lasthealth'] = health.latest('date_alter', 'time_alter')
        except ObjectDoesNotExist:
            pass
    return render(request, 'QuitSoonApp/health.html', context)

def su_ecig(request):
    """Tells if ecig has been selected by user"""
    if request.is_ajax():
        try:
            type_alternative = request.GET['type_alternative_field'].split('=',1)[1]
            substitut = int(request.GET['su_field'].split('=',1)[1])

            if type_alternative == 'Su':
                if Alternative.objects.get(id=substitut).substitut == 'ECIG':
                    return HttpResponse(JsonResponse({'response':'true'}))
            return HttpResponse(JsonResponse({'response':'false'}))
        except:
            return HttpResponse(JsonResponse({'response':'false'}))
    else:
        raise Http404()


def delete_health(request, id_health):
    """
    Used when user click on the trash of one of his healthy action
    """
    if ConsoAlternative.objects.filter(user=request.user, id=id_health).exists():
        data = {'id_health':id_health}
        health = HealthManager(request.user, data)
        health.delete_conso_alternative()
        return redirect('QuitSoonApp:health')
    else:
        raise Http404()

def health_list(request):
    context = {}
    if request.user.is_authenticated:
        # check if packs are in parameters to fill fields with actual packs
        alternatives = Alternative.objects.filter(user=request.user, display=True)
        context['alternatives'] = alternatives
        if alternatives.exists():
            health = ConsoAlternative.objects.filter(user=request.user).order_by('-date_alter', '-time_alter')
            if health.exists():
                health_form = ChooseAlternativeFormWithEmptyFields(request.user)
                if request.method == 'POST':
                    health_form = ChooseAlternativeFormWithEmptyFields(request.user, request.POST)
                    if health_form.is_valid():
                        data = health_form.cleaned_data
                        if data['type_alternative_field'] != 'empty':
                            if data['type_alternative_field'] == 'Su':
                                health = health.filter(alternative__type_alternative=data['type_alternative_field'])
                                if data['su_field'] != 'empty':
                                    alt = Alternative.objects.get(id=int(data['su_field']))
                                    health = health.filter(alternative__substitut=alt.substitut)
                            else:
                                health = health.filter(alternative__type_activity=data['type_alternative_field'])
                                if data['sp_field'] != 'empty':
                                    alt = Alternative.objects.get(id=int(data['sp_field']))
                                    health = health.filter(alternative__activity=alt.activity)
                                elif data['so_field'] != 'empty':
                                    alt = Alternative.objects.get(id=int(data['so_field']))
                                    health = health.filter(alternative__activity=alt.activity)
                                elif data['lo_field'] != 'empty':
                                    alt = Alternative.objects.get(id=int(data['lo_field']))
                                    health = health.filter(alternative__activity=alt.activity)

                context['health_form'] = health_form
                context['health'] = health
    return render(request, 'QuitSoonApp/health_list.html', context)

def report(request, **kwargs):
    """Page with user results, graphs..."""
    context = {}
    if request.user.is_authenticated:

        profile = UserProfile.objects.filter(user=request.user).exists()
        if profile:
            smoke = SmokeStats(request.user, datetime.date.today())
            healthy = HealthyStats(request.user, datetime.date.today())

            # generate context
            context['total_number'] = smoke.total_smoke
            context['average_number'] = round(smoke.average_per_day)
            context['non_smoked'] = smoke.nb_not_smoked_cig
            context['total_money'] = round(smoke.total_money_smoked, 2)
            context['saved_money'] = round(smoke.money_saved, 2)
            context['average_money'] = round(smoke.average_money_per_day, 2)

        else:
            return redirect('QuitSoonApp:profile')
    print(context)
    return render(request, 'QuitSoonApp/report.html', context)

def objectifs(request):
    """Page with user trophees and goals"""
    return render(request, 'QuitSoonApp/objectifs.html')
