from accounts.models import CustomUser
from events.models import Event, EventRegistration
from owner.models import Stall

def pending_requests_badge(request):
    """
    Calculates the total number of pending requests waiting for action 
    based on the currently logged-in user's system role.
    """
    if not request.user.is_authenticated:
        return {'total_pending_count': 0}

    pending_organizers = 0
    pending_events = 0
    pending_vendors = 0
    pending_registrations = 0

    if request.user.role == 'admin':
        pending_organizers = CustomUser.objects.filter(role='student', is_organizer_requested=True).count()
        pending_events = Event.objects.filter(status='pending').count()
        pending_vendors = Stall.objects.filter(is_active=False).exclude(status='rejected').count()
        pending_registrations = EventRegistration.objects.filter(registration_status='pending').count()

    elif request.user.role == 'organizer':
        pending_vendors = Stall.objects.filter(is_active=False, event__organizer=request.user).exclude(status='rejected').count()
        pending_registrations = EventRegistration.objects.filter(
            event__organizer=request.user, registration_status='pending'
        ).count()

    total = pending_organizers + pending_events + pending_vendors + pending_registrations
    return {'total_pending_count': total}