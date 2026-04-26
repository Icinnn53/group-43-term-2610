from django.contrib import admin
from .models import Vendor, Stall


# ================= VENDOR =================
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'social_media')
    search_fields = ('name', 'phone')


# ================= STALL =================
@admin.register(Stall)
class StallAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_name', 'vendor', 'location', 'is_booked')
    list_filter = ('is_booked', 'vendor')
    search_fields = ('event_name', 'location')