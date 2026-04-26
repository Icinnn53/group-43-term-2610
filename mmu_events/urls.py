from django.contrib import admin
from django.urls import path, include

from accounts import views as account_views
from events import views as event_views
from vendor import views as vendor_views


urlpatterns = [
    # ---------------- ADMIN ----------------
    path('admin/', admin.site.urls),

    # ---------------- AUTH ----------------
    path('', account_views.login_view, name='login'),
    path('signup/', account_views.signup_view, name='signup'),
    path('logout/', account_views.logout_view, name='logout'),

    # ---------------- HOME / EVENTS ----------------
    path('home/', event_views.event_list, name='home'),
    path('event/create/', event_views.create_event, name='create_event'),
    path('event/<int:pk>/', event_views.event_detail, name='event_detail'),

    # ---------------- DASHBOARD ----------------
    path('dashboard/', event_views.dashboard, name='dashboard'),

    # ---------------- VENDOR ----------------
    path('vendor/', vendor_views.vendor_list, name='vendor_list'),
    path('vendor/<int:id>/', vendor_views.vendor_detail, name='vendor_detail'),
    path('vendor/<int:id>/edit/', vendor_views.vendor_edit, name='vendor_edit'),

    # ---------------- STALL ----------------
    path('stalls/', vendor_views.stall_list, name='stall_list'),
    path('stalls/create/', vendor_views.stall_create, name='stall_create'),
    path('stalls/<int:id>/edit/', vendor_views.stall_edit, name='stall_edit'),

    # ---------------- VENDOR HOME ----------------
    path('vendor-home/', vendor_views.home, name='vendor_home'),

    # ---------------- LISTINGS ----------------
    path('listings/', include('listings.urls')),
]