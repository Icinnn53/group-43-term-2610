from django.urls import path
from . import views

urlpatterns = [
    # vendor
    path('vendor/', views.vendor_list, name='vendor_list'),
    path('vendor/<int:id>/', views.vendor_detail, name='vendor_detail'),
    path('vendor/<int:id>/edit/', views.vendor_edit, name='vendor_edit'),

    # stall
    path('stalls/', views.stall_list, name='stall_list'),
    path('stalls/create/', views.stall_create, name='stall_create'),
    path('stalls/<int:id>/edit/', views.stall_edit, name='stall_edit'),

    # home
    path('home/', views.home, name='home'),
]