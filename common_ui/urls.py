from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'comui'

urlpatterns = [
    path('', views.index, name='index'),
    path('menu_list/', views.menu_list, name='menu_list'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
]