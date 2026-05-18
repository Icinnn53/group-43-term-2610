from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from .models import Event, EventRegistration
from .forms import (
    EventForm,
    ConcertRegistrationForm,
    TournamentRegistrationForm,
    BazaarRegistrationForm
)

from owner.models import Owner, Stall


# =========================================================
# EVENT LIST
# =========================================================
@login_required
def event_list(request):

    now = timezone.now()
    events = Event.objects.all()

    ongoing, future, past = [], [], []

    for event in events:
        if not event.start_date or not event.end_date:
            ongoing.append(event)
        elif event.end_date < now:
            past.append(event)
        elif event.start_date > now:
            future.append(event)
        else:
            ongoing.append(event)

    return render(request, 'events/event_list.html', {
        'ongoing': ongoing,
        'future': future,
        'past': past,
    })


# =========================================================
# EVENT DETAIL (FIXED OWNERS)
# =========================================================
@login_required
def event_detail(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    if (
        event.status != 'approved'
        and request.user != event.organizer
        and getattr(request.user, 'role', None) != 'admin'
    ):
        messages.warning(request, "This event is not approved yet.")

    is_registered = EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).exists()

    # FIX: owners come from Stall relationship
    owners = Owner.objects.filter(stalls__event=event).distinct()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_registered': is_registered,
        'owners': owners,
        'now': timezone.now(),
    })


# =========================================================
# REGISTER EVENT (AUTO OWNER + STALL FIXED)
# =========================================================
@login_required
def register_event(request, event_id):

    event = get_object_or_404(Event, id=event_id)
    now = timezone.now()

    if event.status != 'approved':
        messages.error(request, "This event is not approved yet.")
        return redirect('event_detail', event_id=event_id)

    if event.end_date and event.end_date < now:
        messages.error(request, "This event has already ended.")
        return redirect('event_detail', event_id=event_id)

    if event.is_full():
        messages.error(request, "Registration is full.")
        return redirect('event_detail', event_id=event_id)

    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "You are already registered for this event.")
        return redirect('event_detail', event_id=event_id)

    form_map = {
        'concert': ConcertRegistrationForm,
        'tournament': TournamentRegistrationForm,
        'bazaar': BazaarRegistrationForm,
    }

    form = form_map.get(event.event_type, ConcertRegistrationForm)(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():

        # 1. Create registration
        EventRegistration.objects.create(
            user=request.user,
            event=event,
            data=form.cleaned_data
        )

        # 2. Create owner
        owner, _ = Owner.objects.get_or_create(
            user=request.user,
            defaults={"name": request.user.username}
        )

        # 3. Create stall (safe linked system)
        Stall.objects.get_or_create(
            event=event,
            owner=owner,
            defaults={
                "name": f"{owner.name}'s Stall",
                "location": event.location,
                "capacity": 1,
                "rental_fee": 0
            }
        )

        messages.success(request, "Successfully registered for event.")
        return redirect('event_detail', event_id=event_id)

    return render(request, 'events/register.html', {
        'form': form,
        'event': event,
    })


# =========================================================
# CANCEL REGISTRATION (ADDED FEATURE)
# =========================================================
@login_required
def cancel_registration(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    registration = EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).first()

    if not registration:
        messages.error(request, "You are not registered for this event.")
        return redirect('event_detail', event_id=event_id)

    if request.method == "POST":
        registration.delete()
        messages.success(request, "Registration cancelled successfully.")
        return redirect('event_detail', event_id=event_id)

    return render(request, 'events/cancel_registration.html', {
        'event': event
    })


# =========================================================
# EDIT EVENT
# =========================================================
@login_required
def edit_event(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    if (
        event.organizer != request.user
        and getattr(request.user, 'role', None) != 'admin'
    ):
        messages.error(request, "Access denied.")
        return redirect('event_detail', event_id=event_id)

    form = EventForm(request.POST or None, request.FILES or None, instance=event)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated successfully.")
        return redirect('event_detail', event_id=event_id)

    return render(request, 'events/edit_event.html', {
        'form': form,
        'event': event
    })


# =========================================================
# DASHBOARD
# =========================================================
@login_required
def dashboard(request):

    registrations = EventRegistration.objects.select_related('event').filter(
        user=request.user
    )

    return render(request, 'events/dashboard.html', {
        'registrations': registrations
    })


# =========================================================
# CREATE EVENT
# =========================================================
@login_required
def create_event(request):

    if getattr(request.user, 'role', None) not in ['organizer', 'admin']:
        messages.error(request, "Access denied.")
        return redirect('home')

    form = EventForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        event = form.save(commit=False)
        event.organizer = request.user
        event.status = 'pending'
        event.save()

        messages.success(request, "Event created successfully.")
        return redirect('home')

    return render(request, 'events/create_event.html', {
        'form': form
    })