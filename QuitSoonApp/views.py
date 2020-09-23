#!/usr/bin/env python

"""QuitSoon Application views"""

import json
import datetime
from datetime import timedelta
import pandas as pd

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, Http404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import F

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from QuitSoonApp.models import (
    UserProfile,
    Paquet, ConsoCig,
    Alternative, ConsoAlternative,
)
from QuitSoonApp.forms import (
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
from QuitSoonApp.modules import (
    ProfileManager,
    PackManager, SmokeManager,
    AlternativeManager, HealthManager,
    SmokeStats, HealthyStats,
    get_delta_last_event,
    TrophyManager,
    DataFrameDate
    )


def index(request):
    """index View"""
    if request.user.is_authenticated:
        return redirect('QuitSoonApp:today')
    return render(request, 'index.html')

def get_client_offset(request):
    """ timezone offset returned by client with django-tz-detect"""
    if request.session.get('detected_tz'):
        return request.session.get('detected_tz')
    return 0

def update_dt_user_model_field(user, tz_offset):
    """update dt_user field in database with actual user time"""
    if tz_offset:
        conso = ConsoCig.objects.filter(user=user)
        conso.update(user_dt=F('datetime_cig') - timedelta(minutes=tz_offset))
        conso = ConsoAlternative.objects.filter(user=user)
        conso.update(user_dt=F('datetime_alter') - timedelta(minutes=tz_offset))

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
    context = {}
    tz_offset = get_client_offset(request)
    smoke_conso = ConsoCig.objects.filter(user=request.user)
    # update user_dt field
    update_dt_user_model_field(request.user, tz_offset)

    if UserProfile.objects.filter(user=request.user).exists():
        context['profile'] = True
        smoke_stats = SmokeStats(request.user, timezone.now(), tz_offset)
        current_tz = timezone.get_current_timezone()
        user_now = current_tz.normalize(timezone.now().astimezone(current_tz))
        if smoke_conso:
            context['smoke_today'] = smoke_stats.nb_per_day(user_now.date())
            last = smoke_conso.latest('datetime_cig').datetime_cig
            context['lastsmoke'] = get_delta_last_event(last)[0]
            context['average_number'] = round(smoke_stats.average_per_day)
    return render(request, 'QuitSoonApp/today.html', context)


def profile(request):
    """User profile page with authentication infos and smoking habits"""
    context = {
        'userprofile':None,
        'user_packs':None,
        }
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
    if request.method == 'POST':
        # make request.POST mutable
        data = dict(request.POST)
        for field in data:
            data[field]=data[field][0]
        # check wich form (existing packs or new pack)
        try:
            if data['ref_pack']:
                existing_pack = True
        except KeyError:
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
            reset = ProfileManager(request.user, parameter_form.cleaned_data)
            reset.new_profile()
        return redirect('QuitSoonApp:profile')
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
            if not request.user.check_password(old_password):
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
    displayed_pack = Paquet.objects.filter(user=request.user, display=True)
    context['form'] = form
    # get packs per type
    context['ind'] = displayed_pack.filter(type_cig='IND')
    context['rol'] = displayed_pack.filter(type_cig='ROL')
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
    tz_offset = get_client_offset(request)
    update_dt_user_model_field(request.user, tz_offset)

    if packs :
        smoke_form = SmokeForm(request.user, tz_offset)
        if request.method == 'POST':
            smoke_form = SmokeForm(request.user, tz_offset,  request.POST)
            if smoke_form.is_valid():
                smoky = SmokeManager(request.user, smoke_form.cleaned_data, tz_offset)
                smoky.create_conso_cig()
                return redirect('QuitSoonApp:today')
        context['smoke_form'] = smoke_form

    smoke_conso = ConsoCig.objects.filter(user=request.user).order_by('-datetime_cig')
    context['smoke'] = smoke_conso
    context['nb_smoke_today']= smoke_conso.filter(datetime_cig__date=timezone.now().date()).count()
    if smoke_conso:
        last = smoke_conso.latest('datetime_cig').datetime_cig
        context['lastsmoke'] = get_delta_last_event(last)
    return render(request, 'QuitSoonApp/smoke.html', context)

def delete_smoke(request, id_smoke):
    """
    Used when user click on the trash of one of his smocke action
    """
    if ConsoCig.objects.filter(user=request.user, id=id_smoke).exists():
        data = {'id_smoke':id_smoke}
        smoky = SmokeManager(request.user, data)
        smoky.delete_conso_cig()
        return redirect('QuitSoonApp:smoke_list')
    raise Http404()

def filter_smoke_to_display(data, smoke_conso):
    """filter smoke list to display user depending on user choice"""
    if data['type_cig_field'] != 'empty':
        if data['type_cig_field'] == 'given':
            smoke_conso = smoke_conso.filter(given=True)
        else:
            smoke_conso = smoke_conso.filter(
                paquet__type_cig=data['type_cig_field']
                )
            if data['ind_pack_field'] != 'empty':
                pack = Paquet.objects.get(id=int(data['ind_pack_field']))
                smoke_conso = smoke_conso.filter(paquet__brand=pack.brand)
            elif data['rol_pack_field'] != 'empty':
                pack = Paquet.objects.get(id=int(data['rol_pack_field']))
                smoke_conso = smoke_conso.filter(paquet__brand=pack.brand)
    return smoke_conso

def smoke_list(request):
    """list conso cig"""
    context = {}
    context['profile'] = UserProfile.objects.filter(user=request.user)
    packs = Paquet.objects.filter(user=request.user, display=True)
    context['packs'] = packs
    # update user_dt field
    tz_offset = get_client_offset(request)
    update_dt_user_model_field(request.user, tz_offset)
    smoke_conso = ConsoCig.objects.filter(user=request.user).order_by('-datetime_cig')
    if packs.exists() and smoke_conso.exists():
        smoke_list_form = ChoosePackFormWithEmptyFields(request.user)
        if request.method == 'POST':
            smoke_list_form = ChoosePackFormWithEmptyFields(request.user, request.POST)
            if smoke_list_form.is_valid():
                data = smoke_list_form.cleaned_data
                smoke_conso = filter_smoke_to_display(data, smoke_conso)
        paginator = Paginator(smoke_conso, 20)
        page = request.GET.get('page')
        page_smoke = paginator.get_page(page)
        context['smoke'] = page_smoke
        context['smoke_list_form'] = smoke_list_form
    return render(request, 'QuitSoonApp/smoke_list.html', context)

def alternatives(request):
    """Healthy parameters, user different activities or substitutes"""
    context = {}
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
    displayed_alt = Alternative.objects.filter(user=request.user, display=True)
    context = {
        'alternative_form':alternative_form,
        'activity_form':activity_form,
        'substitut_form':substitut_form,
        # get packs per type
        'Sp':displayed_alt.filter(type_activity='Sp'),
        'Lo':displayed_alt.filter(type_activity='Lo'),
        'So':displayed_alt.filter(type_activity='So'),
        'Su':displayed_alt.filter(type_alternative='Su'),
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
    raise Http404()

def health(request):
    """User do a healthy activity or uses substitutes"""
    context = {}
    tz_offset = get_client_offset(request)
    # check if alternatives are in parameters to fill fields with actual alternatives
    displayed_alt = Alternative.objects.filter(user=request.user, display=True)
    update_dt_user_model_field(request.user, tz_offset)

    context['alternatives'] = displayed_alt
    if displayed_alt :
        form = HealthForm(request.user, tz_offset)
        if request.method == 'POST':
            form = HealthForm(request.user, tz_offset, request.POST)
            if form.is_valid():
                new_health = HealthManager(request.user, form.cleaned_data, tz_offset)
                new_health.create_conso_alternative()
                return redirect('QuitSoonApp:today')
        context['form'] = form
    healthy = ConsoAlternative.objects.filter(user=request.user).order_by('-datetime_alter')
    context['health'] = healthy
    if healthy:
        last = healthy.latest('datetime_alter').datetime_alter
        context['lasthealth'] = get_delta_last_event(last)
    return render(request, 'QuitSoonApp/health.html', context)

def delete_health(request, id_health):
    """
    Used when user click on the trash of one of his healthy action
    """
    if ConsoAlternative.objects.filter(user=request.user, id=id_health).exists():
        data = {'id_health':id_health}
        healthy = HealthManager(request.user, data)
        healthy.delete_conso_alternative()
        return redirect('QuitSoonApp:health_list')
    raise Http404()

def filter_health_to_display(data, health_conso):
    """filter health list to display user depending on user choice"""
    if data['type_alternative_field'] != 'empty':
        if data['type_alternative_field'] == 'Su':
            health_conso = health_conso.filter(
                alternative__type_alternative=data['type_alternative_field']
                )
            if data['su_field'] != 'empty':
                alt = Alternative.objects.get(id=int(data['su_field']))
                health_conso = health_conso.filter(alternative__substitut=alt.substitut)
        else:
            health_conso = health_conso.filter(
                alternative__type_activity=data['type_alternative_field']
                )
            if data['sp_field'] != 'empty':
                alt = Alternative.objects.get(id=int(data['sp_field']))
                health_conso = health_conso.filter(alternative__activity=alt.activity)
            elif data['so_field'] != 'empty':
                alt = Alternative.objects.get(id=int(data['so_field']))
                health_conso = health_conso.filter(alternative__activity=alt.activity)
            elif data['lo_field'] != 'empty':
                alt = Alternative.objects.get(id=int(data['lo_field']))
                health_conso = health_conso.filter(alternative__activity=alt.activity)
    return health_conso

def health_list(request):
    """Show user saved healthy activities"""
    context = {}
    # check if Alternative are in parameters to fill fields with actual Alternative
    displayed_alt = Alternative.objects.filter(user=request.user, display=True)

    # update user_dt field
    tz_offset = get_client_offset(request)
    update_dt_user_model_field(request.user, tz_offset)

    context['alternatives'] = displayed_alt.exists()
    health_conso = ConsoAlternative.objects.filter(user=request.user).order_by('-datetime_alter')
    if displayed_alt and health_conso.exists():
        health_form = ChooseAlternativeFormWithEmptyFields(request.user)
        if request.method == 'POST':
            health_form = ChooseAlternativeFormWithEmptyFields(request.user, request.POST)
            if health_form.is_valid():
                data = health_form.cleaned_data
                health_conso = filter_health_to_display(data, health_conso)
        paginator = Paginator(health_conso, 20)
        page = request.GET.get('page')
        page_health = paginator.get_page(page)
        context['health'] = page_health
        context['health_form'] = health_form
    return render(request, 'QuitSoonApp/health_list.html', context)

def smoky_report(smoke_stats):
    """user smoking report"""
    stats = {
        'smoke_user_conso_full_days': smoke_stats.user_conso_full_days,
        'total_number': smoke_stats.total_smoke_all_days,
        'average_number': round(smoke_stats.average_per_day),
        'non_smoked': smoke_stats.nb_not_smoked_cig,
        'total_money': round(smoke_stats.total_money_smoked, 2),
        'saved_money': round(smoke_stats.money_saved, 2),
        'average_money': round(smoke_stats.average_money_per_day, 2),
    }
    return stats

def healthy_report(healthy_stats):
    """user healthy activities and substiuts report"""
    stats = {'user_conso_subsitut': healthy_stats.user_conso_subsitut.exists()}
    current_tz = timezone.get_current_timezone()
    user_now = current_tz.normalize(timezone.now().astimezone(current_tz))
    activity_stats = {}
    if healthy_stats.user_activities:
        for type_act in Alternative.TYPE_ACTIVITY:
            activity_stats[type_act[0]] = {}
            conso = ConsoAlternative.objects.filter(alternative__type_activity=type_act[0])
            if conso.exists():
                activity_stats[type_act[0]]['exists'] = True
            activity_stats[type_act[0]]['name'] = type_act[1]
            for period in ['day', 'week', 'month']:
                minutes = healthy_stats.report_alternative_per_period(
                    user_now.date(),
                    period=period,
                    type_alt=type_act[0]
                    )
                str_minutes = healthy_stats.convert_minutes_to_hours_min_str(minutes)
                activity_stats[type_act[0]][period] = str_minutes
        stats['activity_stats'] = activity_stats
    substitut_stats = {}
    if healthy_stats.user_conso_subsitut:
        for type_alt in Alternative.SUBSTITUT:
            substitut_stats[type_alt[0]] = {}
            if ConsoAlternative.objects.filter(alternative__substitut=type_alt[0]).exists():
                substitut_stats[type_alt[0]]['exists'] = True
            substitut_stats[type_alt[0]]['name'] = type_alt[1]
            for period in ['day', 'week', 'month']:
                nicotine = healthy_stats.report_alternative_per_period(
                    user_now.date(),'Su',
                    period=period,
                    type_alt=type_alt[0]
                    )
                substitut_stats[type_alt[0]][period] = nicotine
        stats['substitut_stats'] = substitut_stats
    return stats


def report(request):
    """Page with user results, graphs..."""
    context = {}
    tz_offset = get_client_offset(request)
    update_dt_user_model_field(request.user, tz_offset)
    smoke_stats = SmokeStats(request.user, timezone.now(), tz_offset)
    healthy_stats = HealthyStats(request.user, timezone.now(), tz_offset)
    # graphs with smoke and health activities
    if smoke_stats.user_conso_all_days or healthy_stats.user_conso_all_days:
        # generate context
        context['smoky_report'] = smoky_report(smoke_stats)
        context['healthy_report'] = healthy_report(healthy_stats)
        return render(request, 'QuitSoonApp/report.html', context)
    context['no_data'] = True
    return render(request, 'QuitSoonApp/report.html', context)

def objectifs(request):
    """Page with user trophies and goals"""
    context = {}
    tz_offset = get_client_offset(request)
    stats = SmokeStats(request.user, timezone.now(), tz_offset)
    trophy = TrophyManager(stats)
    trophy.create_trophies()
    context['challenges'] = trophy.user_trophies
    return render(request, 'QuitSoonApp/objectifs.html', context)


class ChartData(APIView):
    """API receiving user choices from client and returning chart data"""
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """API get method"""
        period = request.GET.get('period') or 'Jour'
        charttype = request.GET.get('charttype') or 'nb_cig'
        dates_range = request.GET.get('datesRange') or 0

        smoke_stats = SmokeStats(
            request.user,
            timezone.now(),
            get_client_offset(request)
            )

        if charttype == 'time':

            nb_full_days = smoke_stats.nb_full_days_since_start
            conso_values = smoke_stats.user_conso_full_days.values()
            data_cig = pd.DataFrame(conso_values)
            data = data_cig.user_dt.dt.hour.value_counts()
            data_dict = {}
            for hour in range(0,25):
                try:
                    data_dict[hour] = data.loc[hour] / nb_full_days
                except KeyError:
                    data_dict[hour] = 0
            hour_serie = pd.Series(data_dict)
            result = hour_serie.to_json(orient="split")
            parsed = json.loads(result)
            parsed["data"] = {'base':parsed["data"]}
            parsed["columns"] = 'Moyenne par heure'

        else:

            healthy_stats = HealthyStats(
                request.user,
                timezone.now(),
                get_client_offset(request))

            # generate data for graphs
            user_dict = {'date':[],
                         'activity_duration':[],
                         'nb_cig':[],
                         'money_smoked':[],
                         'nicotine':[]}

            for date in smoke_stats.list_dates:
                user_dict['date'].append(
                    datetime.datetime.combine(date, datetime.datetime.min.time())
                    )
                if healthy_stats.report_alternative_per_period(date):
                    user_dict['activity_duration'].append(
                        healthy_stats.report_alternative_per_period(date)
                        )
                else:
                    user_dict['activity_duration'].append(0)
                if charttype == 'nb_cig':
                    user_dict['nb_cig'].append(smoke_stats.nb_per_day(date))
                elif charttype == 'money_smoked':
                    user_dict['money_smoked'].append(float(smoke_stats.money_smoked_per_day(date)))
                elif charttype == 'nicotine':
                    user_dict['nicotine'].append(healthy_stats.nicotine_per_day(date))
            # keep only usefull keys and value in user_dict
            user_dict = {i:user_dict[i] for i in user_dict if user_dict[i]!=[]}

            df_chart = DataFrameDate(user_dict, charttype)
            if period == 'Jour':
                df_chart = df_chart.day_df
            elif period == 'Semaine':
                df_chart = df_chart.week_df
            elif period == 'Mois':
                df_chart = df_chart.month_df

            if len(df_chart.index) > 7:
                if int(dates_range):
                    df_chart = df_chart.iloc[-7 + int(dates_range): int(dates_range) ]
                else:
                    df_chart = df_chart.tail(7)

            values = df_chart.to_json(orient="values")
            parsed = json.loads(values)
            formated_data = []
            formated_activity_data = []
            for elt in parsed:
                formated_data.append(elt[0])
                formated_activity_data.append(elt[1])

            result = df_chart.to_json(orient="split")
            parsed = json.loads(result)
            parsed["data"] = {'base':formated_data, 'activity':formated_activity_data}
            parsed["min_cig"] = UserProfile.objects.get(user=request.user).starting_nb_cig

        return Response(json.dumps(parsed))
