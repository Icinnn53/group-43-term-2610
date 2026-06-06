from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from events.models import Event
from .models import Owner, Stall


# =========================================================
# OWNER
# =========================================================
def owner_list(request):
    owners = Owner.objects.all()
    return render(request, 'owner/owner_list.html', {'owners': owners})


def owner_detail(request, id):
    owner = get_object_or_404(Owner, id=id)
    return render(request, 'owner/owner_detail.html', {'owner': owner})


def owner_edit(request, id):
    owner = get_object_or_404(Owner, id=id)

    if request.method == "POST":
        owner.name = request.POST.get('name')
        owner.phone = request.POST.get('phone')
        owner.social_media = request.POST.get('social_media')
        owner.description = request.POST.get('description')
        owner.save()

        return redirect('owner_detail', id=owner.id)

    return render(request, 'owner/owner_edit.html', {'owner': owner})


# =========================================================
# STALL
# =========================================================
def stall_list(request):
    query = request.GET.get('q')
    status = request.GET.get('status')

    stalls = Stall.objects.select_related('owner', 'event').all()

    if query:
        stalls = stalls.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(owner__name__icontains=query) |
            Q(event__title__icontains=query)
        )

    if status == "active":
        stalls = stalls.filter(is_active=True)
    elif status == "inactive":
        stalls = stalls.filter(is_active=False)

    return render(request, 'owner/stall_list.html', {
        'stalls': stalls,
        'query': query,
        'status': status
    })


def stall_detail(request, id):
    stall = get_object_or_404(Stall, id=id)
    return render(request, 'owner/stall_detail.html', {'stall': stall})


# =========================================================
# CREATE STALL
# =========================================================
def stall_create(request):
    owner = Owner.objects.first()
    events = Event.objects.all()

    if request.method == "POST":
        event_id = request.POST.get('event_id')

        event = None
        if event_id:
            event = get_object_or_404(Event, id=event_id)

        Stall.objects.create(
            owner=owner,
            event=event,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            location=request.POST.get('location'),
            capacity=int(request.POST.get('capacity') or 1),
            rental_fee=float(request.POST.get('rental_fee') or 0),
            stall_image=request.FILES.get('stall_image'),

            rental_start_date=request.POST.get('rental_start_date') or None,
            rental_end_date=request.POST.get('rental_end_date') or None,
            is_active=True if request.POST.get('is_active') == 'on' else False,
        )

        return redirect('stall_list')

    return render(request, 'owner/stall_create.html', {
        'owner': owner,
        'events': events
    })


# =========================================================
# EDIT STALL
# =========================================================
def stall_edit(request, id):
    stall = get_object_or_404(Stall, id=id)
    events = Event.objects.all()

    if request.method == "POST":
        event_id = request.POST.get('event_id')

        if event_id:
            stall.event = get_object_or_404(Event, id=event_id)
        else:
            stall.event = None

        stall.name = request.POST.get('name')
        stall.description = request.POST.get('description')
        stall.location = request.POST.get('location')
        stall.capacity = int(request.POST.get('capacity') or 1)
        stall.rental_fee = float(request.POST.get('rental_fee') or 0)

        stall.rental_start_date = request.POST.get('rental_start_date') or None
        stall.rental_end_date = request.POST.get('rental_end_date') or None
        stall.is_active = True if request.POST.get('is_active') == 'on' else False

        if request.FILES.get('stall_image'):
            stall.stall_image = request.FILES.get('stall_image')

        stall.save()

        return redirect('stall_detail', id=stall.id)

    return render(request, 'owner/stall_edit.html', {
        'stall': stall,
        'events': events
    })


# =========================================================
# DELETE STALL
# =========================================================
def stall_delete(request, id):
    stall = get_object_or_404(Stall, id=id)

    if request.method == "POST":
        stall.delete()
        return redirect('stall_list')

    return render(request, 'owner/stall_delete.html', {
        'stall': stall
    })


# =========================================================
# EVENT → STALL VIEW
# =========================================================
def stall_by_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    stalls = Stall.objects.select_related('owner').filter(event=event)

    return render(request, 'owner/stall_by_event.html', {
        'event': event,
        'stalls': stalls
    })