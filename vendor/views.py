from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Vendor, Stall
from .forms import VendorForm, StallForm

# ================= VENDOR =================

def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendor/vendor_list.html', {'vendors': vendors})


def vendor_detail(request, id):
    vendor = get_object_or_404(Vendor, id=id)
    stalls = Stall.objects.filter(vendor=vendor)
    return render(request, 'vendor/vendor_detail.html', {
        'vendor': vendor,
        'stalls': stalls
    })


def vendor_edit(request, id):
    vendor = get_object_or_404(Vendor, id=id)
    form = VendorForm(request.POST or None, instance=vendor)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('vendor_list')

    return render(request, 'vendor/vendor_edit.html', {'form': form})


# ================= STALL =================

def stall_list(request):
    stalls = Stall.objects.select_related('vendor').all()
    return render(request, 'vendor/stall_list.html', {'stalls': stalls})


def stall_create(request):
    form = StallForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('stall_list')

    return render(request, 'vendor/stall_create.html', {'form': form})


def stall_edit(request, id):
    stall = get_object_or_404(Stall, id=id)
    form = StallForm(request.POST or None, instance=stall)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('stall_list')

    return render(request, 'vendor/stall_edit.html', {'form': form})


# ================= HOME =================

@login_required
def home(request):
    vendors = Vendor.objects.all()
    stalls = Stall.objects.select_related('vendor').all()

    return render(request, 'vendor/home.html', {
        'vendors': vendors,
        'stalls': stalls,
    })