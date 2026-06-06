from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django import forms

from .models import Event, EventRegistration
from .forms import (
    EventForm,
    ConcertRegistrationForm,
    BazaarRegistrationForm
)

from owner.models import Owner, Stall


# =========================================================
# EVENT LIST
# =========================================================
@login_required
def event_list(request):

    now = timezone.now()
    query = request.GET.get('q')

    events = Event.objects.all()

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query)
        ).distinct()

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
        'query': query
    })


# =========================================================
# EVENT DETAIL
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

    owners = Owner.objects.filter(stalls__event=event).distinct()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_registered': is_registered,
        'owners': owners,
        'now': timezone.now(),
    })


# =========================================================
# REGISTER EVENT
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

    # =====================================================
    # TOURNAMENT (DYNAMIC FORM)
    # =====================================================
    if event.event_type == "tournament":

        class DynamicTournamentForm(forms.Form):
            full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
            email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
            phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                team_size = getattr(event, "team_size", 0) or 0

                for i in range(1, team_size + 1):
                    self.fields[f'player_{i}'] = forms.CharField(
                        label=f'Player {i}',
                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                        required=True
                    )

        form = DynamicTournamentForm(request.POST or None)

    else:
        form_map = {
            'concert': ConcertRegistrationForm,
            'bazaar': BazaarRegistrationForm,
        }

        form_class = form_map.get(event.event_type, ConcertRegistrationForm)
        form = form_class(request.POST or None)

    if request.method == "POST" and form.is_valid():

        EventRegistration.objects.create(
            user=request.user,
            event=event,
            data=form.cleaned_data
        )

        owner, _ = Owner.objects.get_or_create(
            user=request.user,
            defaults={"name": request.user.username}
        )

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
# CANCEL REGISTRATION
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

        Stall.objects.filter(
            event=event,
            owner__user=request.user
        ).delete()

        messages.success(request, "Registration cancelled successfully.")
        return redirect('event_detail', event_id=event_id)

    return redirect('event_detail', event_id=event_id)


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
# STEP 1: SELECT EVENT TYPE
# =========================================================
@login_required
def create_event_select(request):

    if getattr(request.user, 'role', None) not in ['organizer', 'admin']:
        messages.error(request, "Access denied.")
        return redirect('home')

    if request.method == "POST":
        event_type = request.POST.get("event_type")

        if not event_type:
            messages.error(request, "Please select an event type.")
            return redirect('create_event_select')

        return redirect('create_event', event_type=event_type)

    return render(request, 'events/create_event_select.html')


# =========================================================
# STEP 2: CREATE EVENT FORM (FIXED)
# =========================================================
@login_required
def create_event(request, event_type):

    if getattr(request.user, 'role', None) not in ['organizer', 'admin']:
        messages.error(request, "Access denied.")
        return redirect('home')

    form = EventForm(request.POST or None, request.FILES or None)

    # IMPORTANT: ALWAYS PASS event_type SAFE
    event_type = event_type or request.POST.get("event_type")

    if request.method == 'POST' and form.is_valid():

        event = form.save(commit=False)
        event.organizer = request.user
        event.status = 'pending'
        event.event_type = event_type

        # SAVE TEAM SIZE ONLY FOR TOURNAMENT
        if event_type == "tournament":
            event.team_size = int(request.POST.get("team_size", 0))

        event.save()

        messages.success(request, "Event created successfully.")
        return redirect('home')

    return render(request, 'events/create_event.html', {
        'form': form,
        'event_type': event_type
    })