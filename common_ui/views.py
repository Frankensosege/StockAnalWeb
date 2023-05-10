from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from Utilities.comUtilities import get_menu_list
from django.core import serializers

# Create your views here.
def index(request):
    # render the login page
    return render(request, 'common_ui/stock_man_index.html')

# views.py
def menu_list(request):
    # menus = Menu.objects.all()
    # menu_json = serializers.serialize('json', menus)
    menu_json = get_menu_list('aa')
    # return render(request, 'main_menu.html', {'menu_json': menu_json})
    # return JsonResponse(json_post)
    return HttpResponse(menu_json, content_type="application/json")

def login(request):
    pass

def logout(request):
    pass

def signup(request):
    pass