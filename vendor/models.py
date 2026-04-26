from django.db import models
from django.contrib.auth.models import User

# ================= VENDOR =================
class Vendor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    social_media = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# ================= STALL =================
class Stall(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    event_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)

    capacity = models.IntegerField(default=0)
    rental_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event_name} ({self.vendor.name})"