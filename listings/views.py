from django.shortcuts import render, redirect, get_object_or_404
from .models import Listing
from .forms import ListingForm


# LIST
def listing_list(request):
    listings = Listing.objects.all().order_by('-created_at')
    return render(request, 'listings/listing_list.html', {'listings': listings})


# CREATE
def create_listing(request):
    form = ListingForm(request.POST or None)

    if form.is_valid():
        listing = form.save(commit=False)

        if request.user.is_authenticated:
            listing.user = request.user
        else:
            return redirect('login')

        listing.save()
        return redirect('listing_list')

    return render(request, 'listings/create_listing.html', {'form': form})


# DETAIL
def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)
    return render(request, 'listings/listing_detail.html', {'listing': listing})


# EDIT
def edit_listing(request, id):
    listing = get_object_or_404(Listing, id=id)
    form = ListingForm(request.POST or None, instance=listing)

    if form.is_valid():
        form.save()
        return redirect('listing_list')

    return render(request, 'listings/edit_listing.html', {'form': form})


# DELETE
def delete_listing(request, id):
    listing = get_object_or_404(Listing, id=id)

    if request.method == "POST":
        listing.delete()
        return redirect('listing_list')

    return render(request, 'listings/delete_listing.html', {'listing': listing})