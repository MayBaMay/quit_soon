from django.shortcuts import render
from django.contrib.auth import authenticate, login

# Create your views here.

def index(request):
    """index View"""
    return render(request, 'index.html')

def register_view(request):
    """Registration view creating a user and returning json response to ajax"""
    return render(request, 'registration/register.html')
    # response_data = {}
    # if request.method == 'POST':
    #     form = UserCreationFormWithMail(request.POST)
    #     if form.is_valid():
    #         email = request.POST['email']
    #         if User.objects.filter(email=email).exists():
    #             response_data = {'user':"email already in DB"}
    #         else:
    #             form.save()
    #             username = form.cleaned_data.get('username')
    #             raw_password = form.cleaned_data.get('password1')
    #             user = authenticate(username=username, password=raw_password)
    #             login(request, user)
    #             response_data = {'user':"success"}
    #     else:
    #         username = request.POST['username']
    #         password1 = request.POST['password1']
    #         password2 = request.POST['password2']
    #         if password1 != password2:
    #             response_data = {'user':"diff_passwords"}
    #         else:
    #             try:
    #                 user = User.objects.get(username=username)
    #                 response_data = {'user':"already in DB"}
    #             except User.DoesNotExist:
    #                 response_data = {'user':"invalid_password"}
    #     return HttpResponse(JsonResponse(response_data))
    # raise Http404()
