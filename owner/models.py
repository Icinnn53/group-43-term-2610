from django.db import models
from django.conf import settings


# =========================================================
# OWNER MODEL
# =========================================================
class Owner(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owners"
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    social_media = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# =========================================================
# STALL MODEL
# =========================================================
class Stall(models.Model):

    # ✅ OPTIONAL EVENT
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="stalls",
        null=True,
        blank=True
    )

    owner = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        related_name="stalls",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)

    capacity = models.PositiveIntegerField(default=1)

    rental_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # ✅ STALL IMAGE
    stall_image = models.ImageField(
        upload_to="stall_images/",
        blank=True,
        null=True
    )

    # ✅ RENTAL DATE
    rental_start_date = models.DateField(blank=True, null=True)
    rental_end_date = models.DateField(blank=True, null=True)

    # ✅ NEW STALLS ARE INACTIVE FIRST
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        event_name = self.event.title if self.event else "No Event"
        return f"{self.name} ({event_name})"