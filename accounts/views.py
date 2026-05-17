from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfessionalSignupForm
from .models import CustomUser 
from events.models import Event
from owner.models import Stall

def signup_view(request):
    if request.method == 'POST':
        form = ProfessionalSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = ProfessionalSignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'accounts/logout_confirm.html')

#adminview
@login_required
def profile_view(request):
    context = {'user': request.user}
    return render(request, 'accounts/profile.html', context)

#requestorganizer
@login_required
def request_organizer_view(request):
    if request.method == 'POST':
        user = request.user
    
        if user.role == 'student' and not user.is_rejected:
            user.is_organizer_requested = True
            user.save()
            messages.success(request, "Request sent to Admin.")
        else:
            messages.error(request, "You are not eligible to request this role.")
        return redirect('profile')
    return redirect('profile')

#approveorganizer
@login_required
def approve_organizer_view(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, "Access Denied.")
        return redirect('home')
    
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        target_user.role = 'organizer'
        target_user.is_organizer_requested = False
        target_user.is_rejected = False 
        target_user.save()
        messages.success(request, f"{target_user.username} is now an Organizer!")
    
    return redirect('pending_requests')

#rejectorganizer
@login_required
def reject_organizer_view(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, "Access Denied.")
        return redirect('home')
    
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        target_user.is_organizer_requested = False
        target_user.is_rejected = True
        target_user.save()
        messages.warning(request, f"Request for {target_user.username} has been rejected.")
    
    return redirect('pending_requests')

@login_required
def pending_requests_view(request):
    context = {}
    if request.user.role == 'admin':
        context['pending_organizers'] = CustomUser.objects.filter(role='student', is_organizer_requested=True)
        context['pending_events'] = Event.objects.filter(status='pending')
        context['pending_vendors'] = Stall.objects.filter(is_active=False)
    elif request.user.role == 'organizer':
        context['pending_vendors'] = Stall.objects.filter(is_active=False, event__organizer=request.user)
    else:
        messages.error(request, "Access Denied.")
        return redirect('home')
    return render(request, 'accounts/pending_requests.html', context)

#Approve Event View
@login_required
def approve_event_view(request, event_id):
    if request.user.role != 'admin':
        messages.error(request, "Access Denied.")
        return redirect('home')
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        event.status = 'approved'
        event.save()
        messages.success(request, f"Event '{event.title}' has been successfully approved and is live!")
    return redirect('pending_requests')

#Reject Event View
@login_required
def reject_event_view(request, event_id):
    if request.user.role != 'admin':
        messages.error(request, "Access Denied.")
        return redirect('home')
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        event.status = 'rejected'
        event.save()
        messages.warning(request, f"Event '{event.title}' request was rejected.")
    return redirect('pending_requests')

#View Pending Event Full Details
@login_required
def pending_event_detail_view(request, event_id):
    if request.user.role != 'admin':
        messages.error(request, "Access Denied.")
        return redirect('home')
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'accounts/pending_event_detail.html', {'event': event})