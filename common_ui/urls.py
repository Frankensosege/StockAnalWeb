from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'comui'

urlpatterns = [
    path('', views.index, name='index'),
    path('welcome', views.welcome, name='welcome'),
    path('menu_list/', views.menu_list, name='menu_list'),
    path('login/', views.login_sys, name='login'),
    path('logout/', views.logout_sys, name='logout'),
    path('signup/', views.signup, name='signup'),
]