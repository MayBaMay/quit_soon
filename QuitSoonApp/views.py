from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm


# Create your views here.

def index(request):
    """index View"""
    return render(request, 'index.html')

def register(request):
    """Registration view creating a user and returning json response to ajax"""
    response_data = {}
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            response_data = {'response':"success"}
        else:
            emil = request.POST['emil']
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if User.objects.filter(username=username).exists():
                response_data = {'response':"username already in DB"}
            elif User.objects.filter(email=email).exists():
                response_data = {'response':"email already in DB"}
            elif password1 != password2:
                response_data = {'response':"passwords diff"}
            else:
                response_data = {'response':"invalid password"}
        return HttpResponse(JsonResponse(response_data))
    else:
        return render(request, 'registration/register.html')

def login(request):
    """Login view returning json response to ajax"""
    return render(request, 'registration/login.html')
    response_data = {}
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            username = form.get_user()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                response_data = {'user':"success"}
            else:
                response_data = {'user':"error-user-none"}
        else:
            username = request.POST['username']
            password = request.POST['password']
            try:
                user = User.objects.get(username=username)
                if user.password != password:
                    response_data = {'user':"wrong_password"}
                else:
                    response_data = {'user':"error"}
            except User.DoesNotExist:
                response_data = {'user':"user_unknown"}
        return HttpResponse(JsonResponse(response_data))
    raise Http404()
