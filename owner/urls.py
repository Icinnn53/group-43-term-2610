from django.urls import path
from . import views

urlpatterns = [

    # ================= OWNER =================
    path('', views.owner_list, name='owner_list'),
    path('owners/create/', views.owner_create, name='owner_create'),
    path('owners/<int:id>/', views.owner_detail, name='owner_detail'),
    path('owners/<int:id>/edit/', views.owner_edit, name='owner_edit'),

    # ================= STALL =================
    path('stalls/', views.stall_list, name='stall_list'),
    path('stalls/create/', views.stall_create, name='stall_create'),
    path('stalls/<int:id>/', views.stall_detail, name='stall_detail'),
    path('stalls/<int:id>/edit/', views.stall_edit, name='stall_edit'),
    path('stalls/<int:id>/delete/', views.stall_delete, name='stall_delete'),
    path('stalls/<int:id>/approve/', views.stall_approve, name='stall_approve'),

    # ✅ Rejected Stall List
    path('stalls/rejected/', views.rejected_stall_list, name='rejected_stall_list'),

    # ================= EVENT → STALLS =================
    path('events/<int:event_id>/stalls/', views.stall_by_event, name='stall_by_event'),
]
