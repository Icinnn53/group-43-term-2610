from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as account_views
from events import views as event_views
from owner import views as owner_views


urlpatterns = [

    # ================= ADMIN =================
    path('admin/', admin.site.urls),

    # ================= AUTH =================
    path('', account_views.login_view, name='login'),
    path('signup/', account_views.signup_view, name='signup'),
    path('logout/', account_views.logout_view, name='logout'),
    path('profile/', account_views.profile_view, name='profile'),

    path('profile/request-organizer/', account_views.request_organizer_view, name='request_organizer'),
    path('profile/approve/<int:user_id>/', account_views.approve_organizer_view, name='approve_organizer'),
    path('profile/reject/<int:user_id>/', account_views.reject_organizer_view, name='reject_organizer'),
    path('profile/pending-requests/', account_views.pending_requests_view, name='pending_requests'),
    path('profile/pending-requests/event/<int:event_id>/', account_views.pending_event_detail_view, name='pending_event_detail'),
    path('profile/pending-requests/event/<int:event_id>/approve/', account_views.approve_event_view, name='approve_event'),
    path('profile/pending-requests/event/<int:event_id>/reject/', account_views.reject_event_view, name='reject_event'),

    # ======= ADDED STALL ROUTING CHANNELS (MATCHING MECHANICS ABOVE) =======
    path('profile/stall/detail/<int:stall_id>/', account_views.pending_stall_detail_view, name='pending_stall_detail'),
    path('profile/stall/approve/<int:stall_id>/', account_views.approve_stall_view, name='approve_stall'),
    path('profile/stall/reject/<int:stall_id>/', account_views.reject_stall_view, name='reject_stall'),

    # ================= EVENTS =================
    path('home/', event_views.event_list, name='home'),
    path('dashboard/', event_views.dashboard, name='dashboard'),

    # ✅ NEW: STEP 1 (choose event type)
    path('event/create/', event_views.create_event_select, name='create_event_select'),

    # ✅ STEP 2 (actual form)
    path('event/create/<str:event_type>/', event_views.create_event, name='create_event'),

    path('event/<int:event_id>/', event_views.event_detail, name='event_detail'),
    path('event/<int:event_id>/edit/', event_views.edit_event, name='edit_event'),

    path('event/<int:event_id>/register/', event_views.register_event, name='register_event'),

    path(
        'event/<int:event_id>/cancel/',
        event_views.cancel_registration,
        name='cancel_registration'
    ),

    # ================= OWNER =================
    path('owners/', owner_views.owner_list, name='owner_list'),
    path('owners/<int:id>/', owner_views.owner_detail, name='owner_detail'),
    path('owners/<int:id>/edit/', owner_views.owner_edit, name='owner_edit'),

    # ================= STALL =================
    path('stalls/', owner_views.stall_list, name='stall_list'),
    path('stalls/create/', owner_views.stall_create, name='stall_create'),
    path('stalls/<int:id>/', owner_views.stall_detail, name='stall_detail'),
    path('stalls/<int:id>/edit/', owner_views.stall_edit, name='stall_edit'),
    path('stalls/<int:id>/delete/', owner_views.stall_delete, name='stall_delete'),

    path('event/<int:event_id>/stalls/', owner_views.stall_by_event, name='stall_by_event'),

    # ================= PRODUCTS =================
    path('products/', include('products.urls')),
]


# ================= MEDIA =================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)