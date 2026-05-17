from django.urls import path
from . import views

urlpatterns = [
    
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('request-organizer/', views.request_organizer_view, name='request_organizer'),
    path('approve/<int:user_id>/', views.approve_organizer_view, name='approve_organizer'),
    path('profile/reject/<int:user_id>/', views.reject_organizer_view, name='reject_organizer'),
    path('profile/pending-requests/', views.pending_requests_view, name='pending_requests'),
]