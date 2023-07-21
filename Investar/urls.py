from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'investar'

urlpatterns = [
    path('get_paged_item/', views.get_paged_item, name='get_paged_item'),
    path('total_item_count/', views.total_item_count, name='total_item_count'),
    path('retrieve_portpolio/', views.retrieve_portpolio, name='retrieve_portpolio'),
    path('create_portpolio/', views.create_portpolio, name='create_portpolio'),
    path('save_investitem/', views.save_investitem, name='save_investitem'),
    path('tool_man/', views.tool_man, name='tool_man'),

]