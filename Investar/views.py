from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from Utilities.comUtilities import get_menu_list
# from .forms import UserForm, UsrCreationForm

def inv_item(request):
    menu_json = get_menu_list(request.session.get('auth'))

    return HttpResponse(menu_json, content_type="application/json")
