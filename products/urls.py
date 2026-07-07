from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),

    path('stall/<int:stall_id>/', views.product_by_stall, name='product_by_stall'),

    path('add/', views.product_create, name='product_create'),

    path('edit/<int:id>/', views.edit_product, name='edit_product'),

    path('delete/<int:id>/', views.delete_product, name='delete_product'),

    path('<int:id>/', views.product_detail, name='product_detail'),
]