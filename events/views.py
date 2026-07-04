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
    PaymentReceiptForm,
)

from owner.models import Owner, Stall


# =========================================================
# EVENT LIST
# =========================================================
@login_required
def event_list(request):

    query = request.GET.get("q")
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

    registration = EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).first()

    owners = Owner.objects.filter(stalls__event=event).distinct()

    return render(request, "events/event_detail.html", {
        "event": event,
        "is_registered": is_registered,
        "is_vendor": is_vendor,
        "registration": registration,
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
# REGISTER EVENT
# =========================================================
@login_required
def register_event(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    # --- NEW: block registration for past events ---
    if event.is_past():
        messages.error(request, "This event has already ended. Registration is closed.")
        return redirect("event_detail", event_id=event_id)

    if event.status != "approved":
        messages.error(request, "Event not approved.")
        return redirect("event_detail", event_id=event_id)

    if event.is_full():
        messages.error(request, "Event is full.")
        return redirect("event_detail", event_id=event_id)

    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "Already registered.")
        return redirect("event_detail", event_id=event_id)

    if event.event_type == "tournament":

        class TournamentForm(forms.Form):
            full_name = forms.CharField()
            email = forms.EmailField()
            phone_number = forms.CharField()

            team_member_1 = forms.CharField(label="Team Member 1", required=True)
            team_member_2 = forms.CharField(label="Team Member 2", required=False)
            team_member_3 = forms.CharField(label="Team Member 3", required=False)
            team_member_4 = forms.CharField(label="Team Member 4", required=False)
            team_member_5 = forms.CharField(label="Team Member 5", required=False)
            team_member_6 = forms.CharField(label="Team Member 6", required=False)
            team_member_7 = forms.CharField(label="Team Member 7", required=False)
            team_member_8 = forms.CharField(label="Team Member 8", required=False)
            team_member_9 = forms.CharField(label="Team Member 9", required=False)
            team_member_10 = forms.CharField(label="Team Member 10", required=False)
            team_member_11 = forms.CharField(label="Team Member 11", required=False)

        form = TournamentForm(request.POST or None)

    else:
        form_class = {
            "concert": ConcertRegistrationForm,
            "bazaar": BazaarRegistrationForm,
        }.get(event.event_type, ConcertRegistrationForm)

        form = form_class(request.POST or None)

    if request.method == "POST" and form.is_valid():

        # registration_status defaults to "pending" on the model — organiser
        # must explicitly approve, regardless of whether there's a fee.
        payment_status = "pending" if event.has_fee() else "not_required"

        EventRegistration.objects.create(
            user=request.user,
            event=event,
            data=form.cleaned_data,
            payment_status=payment_status
        )

        if event.has_fee():
            return redirect("payment", event_id=event_id)

        messages.success(request, "Registration submitted! Waiting for organizer approval.")
        return redirect("event_detail", event_id=event_id)

    return render(request, "events/register.html", {
        "form": form,
        "event": event,
    })


# =========================================================
# PAYMENT VIEW
# =========================================================
@login_required
def payment_view(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    registration = EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).first()

    if not registration:
        messages.error(request, "You are not registered for this event.")
        return redirect("event_detail", event_id=event_id)

    if registration.registration_status == "approved":
        messages.info(request, "Your registration is already approved.")
        return redirect("event_detail", event_id=event_id)

    form = PaymentReceiptForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        registration.payment_receipt = form.cleaned_data["payment_receipt"]
        registration.payment_status = "pending"
        registration.save()

        messages.success(request, "Receipt uploaded! Waiting for organizer approval.")
        return redirect("event_detail", event_id=event_id)

    return render(request, "events/payment.html", {
        "form": form,
        "event": event,
        "registration": registration,
    })


# =========================================================
# REGISTER VENDOR
# =========================================================
@login_required
def register_vendor(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    # --- NEW: block vendor registration for past events ---
    if event.is_past():
        messages.error(request, "This event has already ended. Vendor registration is closed.")
        return redirect("event_detail", event_id=event_id)

    if not event.allow_vendors_collaborators:
        messages.error(request, "Vendor registration is disabled.")
        return redirect("event_detail", event_id=event_id)

    if VendorRegistration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "Already registered as vendor.")
        return redirect("event_detail", event_id=event_id)

    form = VendorRegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

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


# =========================================================
# REGISTRATION APPROVAL (display lives in accounts.pending_requests_view)
# =========================================================

@login_required
def approve_registration(request, registration_id):

    registration = get_object_or_404(EventRegistration, id=registration_id)

    if request.user != registration.event.organizer and getattr(request.user, "role", None) != "admin":
        messages.error(request, "Access denied.")
        return redirect("home")

    if request.method == "POST":
        registration.registration_status = "approved"
        if registration.event.has_fee():
            registration.payment_status = "approved"
        registration.save()
        messages.success(request, f"Registration approved for {registration.user.username}.")

    return redirect("pending_requests")


@login_required
def reject_registration(request, registration_id):

    registration = get_object_or_404(EventRegistration, id=registration_id)

    if request.user != registration.event.organizer and getattr(request.user, "role", None) != "admin":
        messages.error(request, "Access denied.")
        return redirect("home")

    if request.method == "POST":
        registration.registration_status = "rejected"
        if registration.event.has_fee():
            registration.payment_status = "rejected"
        registration.save()
        messages.error(request, f"Registration rejected for {registration.user.username}.")

    return redirect("pending_requests")