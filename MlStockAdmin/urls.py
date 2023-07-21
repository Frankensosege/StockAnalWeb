from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'stkadmin'

urlpatterns = [
    path('get_paged_item/', views.get_paged_item, name='get_paged_item'),
    path('total_item_count/', views.total_item_count, name='total_item_count'),
    path('save_item_price/', views.save_item_price, name='save_item_price'),
    path('item_admin/', views.item_admin, name='item_admin'),
    path('item_fss/', views.item_fss, name='item_fss'),
    path('item_learn/', views.item_learn, name='item_learn'),
    path('save_item_learn/', views.save_item_learn, name='save_item_learn'),
    path('save_item_fss/', views.save_item_fss, name='save_item_fss'),
    path('item_learn_model/', views.item_learn_model, name='item_learn_model'),
    path('item_prediction/', views.item_prediction, name='item_prediction'),
    path('anal_tool_man/', views.anal_tool_man, name='anal_tool_man'),
    path('total_tool_count/', views.total_tool_count, name='total_tool_count'),
    path('get_paged_tool/', views.get_paged_tool, name='get_paged_tool'),
    path('save_tool/', views.save_tool, name='save_tool'),
    path('delete_tool/', views.delete_tool, name='delete_tool'),
    path('show_tool/', views.show_tool, name='show_tool'),

]