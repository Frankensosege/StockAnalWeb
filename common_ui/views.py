from django.shortcuts import render
from django.core import serializers

# Create your views here.
def index(request):
    # render the login page
    return render(request, 'common_ui/stock_man_index.html')

# views.py
def menu_list(request):
    menus = Menu.objects.all()
    menu_json = serializers.serialize('json', menus)
    return render(request, 'menu_list.html', {'menu_json': menu_json})


def login(request):
    pass

def logout(request):
    pass

def signup(request):
    pass