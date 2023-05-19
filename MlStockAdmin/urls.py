from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'stkadmin'

urlpatterns = [
    path('get_paged_item/', views.get_paged_item, name='get_paged_item'),
    path('total_item_count/', views.total_item_count, name='total_item_count'),
    path('save_item_price/', views.save_item_price, name='save_item_price'),
    path('item_admin/', views.item_admin, name='item_admin'),

]