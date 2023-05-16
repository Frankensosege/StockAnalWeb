from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'investar'

urlpatterns = [
    path('', views.inv_item, name='inv_item'),
]