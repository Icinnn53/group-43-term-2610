from django import forms
from .models import Vendor, Stall

# ===== VENDOR FORM =====
class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'phone', 'social_media', 'description']


# ===== STALL FORM =====
class StallForm(forms.ModelForm):
    class Meta:
        model = Stall
        fields = ['vendor', 'event_name', 'location', 'capacity', 'rental_fee', 'is_booked']