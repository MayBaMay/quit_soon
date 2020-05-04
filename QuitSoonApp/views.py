from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, Http404

from .forms import RegistrationForm


# Create your views here.

def index(request):
    """index View"""
    return render(request, 'index.html')

def register_view(request):
    """Registration view creating a user and returning json response to ajax"""
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
    """Login view returning json response to ajax"""
    # response_data = {}
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                print('user is not none' )
                login(request, user)
                return redirect('index.html')
            #     response_data = {'response':"success"}
            # else:
            #     response_data = {'response':"error-user-none"}
            print('user is none' )
        # else:
        #     email = request.POST['email']
        #     password = request.POST['password']
        #     try:
        #         user = User.objects.get(email=email)
        #         if user.password != password:
        #             response_data = {'response':"wrong_password"}
        #         else:
        #             response_data = {'response':"error"}
        #     except User.DoesNotExist:
        #         response_data = {'response':"user_unknown"}
        # return HttpResponse(JsonResponse(response_data))
    return render(request, 'registration/login.html', {'form':form})
