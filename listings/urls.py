from django.urls import path
from . import views

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('create/', views.create_listing, name='create_listing'),
    path('<int:id>/', views.listing_detail, name='listing_detail'),
    path('<int:id>/edit/', views.edit_listing, name='edit_listing'),
    path('<int:id>/delete/', views.delete_listing, name='delete_listing'),
]