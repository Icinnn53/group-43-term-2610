from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django import forms

from .models import Event, EventRegistration, VendorRegistration
from .forms import (
    EventForm,
    ConcertRegistrationForm,
    BazaarRegistrationForm,
    VendorRegistrationForm,
)

from owner.models import Owner, Stall


# =========================================================
# EVENT LIST
# =========================================================
@login_required
def event_list(request):

    query = request.GET.get("q")
    # FIX: Only fetch approved events so pending ones don't throw off the count statistics
    events = Event.objects.filter(status="approved")

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query)
        )

    now = timezone.now()
    ongoing, future, past = [], [], []

    for event in events:
        if event.end_date and event.end_date < now:
            past.append(event)
        elif event.start_date and event.start_date > now:
            future.append(event)
        else:
            ongoing.append(event)

    return render(request, "events/event_list.html", {
        "ongoing": ongoing,
        "future": future,
        "past": past,
        "query": query
    })


# =========================================================
# EVENT DETAIL
# =========================================================
@login_required
def event_detail(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    is_registered = EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).exists()

    is_vendor = VendorRegistration.objects.filter(
        user=request.user,
        event=event
    ).exists()

    owners = Owner.objects.filter(stalls__event=event).distinct()

    return render(request, "events/event_detail.html", {
        "event": event,
        "is_registered": is_registered,
        "is_vendor": is_vendor,
        "owners": owners,
        "now": timezone.now(),
    })


# =========================================================
# DASHBOARD
# =========================================================
@login_required
def dashboard(request):

    registrations = EventRegistration.objects.select_related("event").filter(
        user=request.user
    )

    return render(request, "events/dashboard.html", {
        "registrations": registrations
    })


# =========================================================
# CREATE EVENT SELECT
# =========================================================
@login_required
def create_event_select(request):

    if getattr(request.user, "role", None) not in ["organizer", "admin"]:
        messages.error(request, "Access denied.")
        return redirect("home")

    if request.method == "POST":
        event_type = request.POST.get("event_type")

        if not event_type:
            messages.error(request, "Please select event type.")
            return redirect("create_event_select")

        return redirect("create_event", event_type=event_type)

    return render(request, "events/create_event_select.html")


# =========================================================
# CREATE EVENT
# =========================================================
@login_required
def create_event(request, event_type):

    if getattr(request.user, "role", None) not in ["organizer", "admin"]:
        messages.error(request, "Access denied.")
        return redirect("home")

    form = EventForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():

        event = form.save(commit=False)

        event.organizer = request.user
        event.status = "pending"
        event.event_type = event_type

        if event_type == "tournament":
            event.team_size = request.POST.get("team_size") or None

        event.save()

        messages.success(request, "Event created successfully.")
        return redirect("home")

    return render(request, "events/create_event.html", {
        "form": form,
        "event_type": event_type
    })


# =========================================================
# EDIT EVENT
# =========================================================
@login_required
def edit_event(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    if event.organizer != request.user and getattr(request.user, "role", None) != "admin":
        messages.error(request, "Access denied.")
        return redirect("event_detail", event_id=event_id)

    form = EventForm(request.POST or None, request.FILES or None, instance=event)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated successfully.")
        return redirect("event_detail", event_id=event_id)

    return render(request, "events/edit_event.html", {
        "form": form,
        "event": event
    })


# =========================================================
# REGISTER EVENT (ATTENDEE) — FIXED
# =========================================================
@login_required
def register_event(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    if event.status != "approved":
        messages.error(request, "Event not approved.")
        return redirect("event_detail", event_id=event_id)

    if event.is_full():
        messages.error(request, "Event is full.")
        return redirect("event_detail", event_id=event_id)

    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "Already registered.")
        return redirect("event_detail", event_id=event_id)

    # ---- FORM ----
    if event.event_type == "tournament":

        class TournamentForm(forms.Form):
            full_name = forms.CharField()
            email = forms.EmailField()
            phone_number = forms.CharField()

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for i in range(1, (event.team_size or 0) + 1):
                    self.fields[f"player_{i}"] = forms.CharField()

        form = TournamentForm(request.POST or None)

    else:
        form_class = {
            "concert": ConcertRegistrationForm,
            "bazaar": BazaarRegistrationForm,
        }.get(event.event_type, ConcertRegistrationForm)

        form = form_class(request.POST or None)

    # ---- SAVE ----
    if request.method == "POST" and form.is_valid():

        EventRegistration.objects.create(
            user=request.user,
            event=event,
            data=form.cleaned_data
        )

        # ❌ FIX: NO MORE STALL CREATION HERE
        messages.success(request, "Registered successfully.")
        return redirect("event_detail", event_id=event_id)

    return render(request, "events/register.html", {
        "form": form,
        "event": event,
    })


# =========================================================
# REGISTER VENDOR (CORRECT)
# =========================================================
@login_required
def register_vendor(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    # =========================
    # DEBUG LOGS (IMPORTANT)
    # =========================
    print("\n========== VENDOR DEBUG ==========")
    print("Event ID:", event.id)
    print("User:", request.user)
    print("Allow vendors:", event.allow_vendors_collaborators)
    print("Request method:", request.method)
    print("==================================\n")

    # =========================
    # FEATURE CHECK
    # =========================
    if not event.allow_vendors_collaborators:
        print("BLOCKED: vendor disabled for this event")

        messages.error(request, "Vendor registration is disabled.")
        return redirect("event_detail", event_id=event_id)

    # =========================
    # ALREADY REGISTERED CHECK
    # =========================
    exists = VendorRegistration.objects.filter(
        user=request.user,
        event=event
    ).exists()

    print("Already vendor registered:", exists)

    if exists:
        messages.warning(request, "Already registered as vendor.")
        return redirect("event_detail", event_id=event_id)

    # =========================
    # FORM
    # =========================
    form = VendorRegistrationForm(request.POST or None)

    print("Form valid:", form.is_valid() if request.method == "POST" else "GET request")

    # =========================
    # SAVE
    # =========================
    if request.method == "POST" and form.is_valid():

        print("FORM DATA:", form.cleaned_data)

        VendorRegistration.objects.create(
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
                "name": form.cleaned_data.get("stall_name"),
                "location": event.location,
                "capacity": 1,
                "rental_fee": 0
            }
        )

        print("SUCCESS: Vendor registered")

        messages.success(request, "Vendor registered successfully.")
        return redirect("event_detail", event_id=event_id)

    return render(request, "events/register_vendor.html", {
        "form": form,
        "event": event,
    })


# =========================================================
# CANCEL ATTENDEE
# =========================================================
@login_required
def cancel_registration(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    get_reg = EventRegistration.objects.filter(user=request.user, event=event).first()

    if request.method == "POST" and get_reg:
        get_reg.delete()
        messages.success(request, "Registration cancelled.")
        return redirect("event_detail", event_id=event_id)

    return redirect("event_detail", event_id=event_id)


# =========================================================
# CANCEL VENDOR
# =========================================================
@login_required
def cancel_vendor_registration(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    get_reg = VendorRegistration.objects.filter(user=request.user, event=event).first()

    if request.method == "POST" and get_reg:
        get_reg.delete()
        messages.success(request, "Vendor registration cancelled.")
        return redirect("event_detail", event_id=event_id)

    return redirect("event_detail", event_id=event_id)