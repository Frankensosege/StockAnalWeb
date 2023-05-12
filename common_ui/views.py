from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from Utilities.comUtilities import get_menu_list
from .forms import UserForm

# Create your views here.
def index(request):
    # render the login page
    return render(request, 'common_ui/stock_man_index.html')

# views.py
def menu_list(request):
    # menus = Menu.objects.all()
    # menu_json = serializers.serialize('json', menus)
    menu_json = get_menu_list('B')
    # return render(request, 'main_menu.html', {'menu_json': menu_json})
    # return JsonResponse(json_post)
    return HttpResponse(menu_json, content_type="application/json")

def login(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        # user_name = request.POST.get('user_name')
        passwd = request.POST.get('passwd')

        # query the database for the user with the given username and password
        # user = User.objects.get(email=email, passwd=passwd)
        user = authenticate(email=email, password=passwd)

        if user is not None:
            # redirect the user to the home page
            request.session['email'] = user.email
            # redirect_to = reverse('login:welcome', kwargs={'name':user.user_name})
            if user.user_name is None or user.user_name == "":
                request.session['user_name'] = user.user_name
                user_name = user.user_name
            return redirect('comui:welcome', {'user_name': user_name})
            # return HttpResponseRedirect(redirect_to)
        else:
            # display an error message
            error = 'Invalid credentials. Please try again.'

    else:
        form = UserForm()

    # render the login page
    return render(request, 'common_ui/login.html', {'form': form})

def logout(request):
    pass

def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserForm()
    return render(request, 'common_ui/signup.html', {'form': form})

def welcome(request, user_name):
    pass