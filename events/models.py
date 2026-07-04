from django.db import models
from django.conf import settings
from django.utils import timezone


# =========================================================
# EVENT
# =========================================================
class Event(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    EVENT_TYPE_CHOICES = [
        ('concert', 'Concert'),
        ('tournament', 'Tournament'),
        ('bazaar', 'Bazaar'),
    ]

    # ------------------------
    # BASIC INFO
    # ------------------------
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    image = models.ImageField(
        upload_to='events/',
        null=True,
        blank=True
    )

    # ------------------------
    # ORGANIZER
    # ------------------------
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # ------------------------
    # REGISTRATION SETTINGS
    # ------------------------
    allow_registration = models.BooleanField(default=True)

    max_registrations = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    allow_vendors_collaborators = models.BooleanField(default=False)

    # ------------------------
    # FEES
    # ------------------------
    enable_registration_fee = models.BooleanField(default=False)

    registration_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True
    )

    # ------------------------
    # PAYMENT DETAILS
    # ------------------------
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)

    # ------------------------
    # TOURNAMENT ONLY
    # ------------------------
    team_size = models.PositiveIntegerField(null=True, blank=True)

    # ------------------------
    # TIMESTAMP
    # ------------------------
    created_at = models.DateTimeField(auto_now_add=True)

    # =====================================================
    # HELPERS
    # =====================================================
    def total_registrations(self):
        count = self.registrations.filter(
            registration_status="approved"
        ).count()
        # Bazaar events count approved vendor sign-ups toward the
        # total/registration cap as well as attendees.
        if self.event_type == "bazaar":
            count += self.vendor_registrations.count()
        return count

    def is_full(self):
        if not self.max_registrations:
            return False
        return self.total_registrations() >= self.max_registrations

    def has_fee(self):
        return (
            self.enable_registration_fee
            and self.registration_fee is not None
            and self.registration_fee > 0
        )

    def is_past(self):
        """
        An event is considered 'past' once its end_date has passed.
        Used to block new registrations for events that already happened.
        """
        return self.end_date < timezone.now()

    def can_register(self):
        """
        Central place to decide if registration is currently allowed.
        Combines the past-event check with the existing allow_registration flag.
        """
        return self.allow_registration and not self.is_past()

    def __str__(self):
        return self.title


# =========================================================
# EVENT REGISTRATION (ATTENDEE)
# =========================================================
class EventRegistration(models.Model):

    # ------------------------
    # REGISTRATION STATUS (NEW CORE FEATURE)
    # ------------------------
    REGISTRATION_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    PAYMENT_STATUS = [
        ('not_required', 'Not Required'),
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    data = models.JSONField(blank=True, null=True)

    registered_at = models.DateTimeField(auto_now_add=True)

    # ------------------------
    # REGISTRATION APPROVAL (IMPORTANT)
    # ------------------------
    registration_status = models.CharField(
        max_length=20,
        choices=REGISTRATION_STATUS,
        default='pending'
    )

    # ------------------------
    # PAYMENT
    # ------------------------
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='not_required'
    )

    payment_receipt = models.ImageField(
        upload_to='receipts/',
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('user', 'event')

    # =====================================================
    # HELPERS
    # =====================================================
    def is_pending(self):
        return self.registration_status == "pending"

    def is_approved(self):
        return self.registration_status == "approved"

    def is_rejected(self):
        return self.registration_status == "rejected"

    def payment_required(self):
        return self.event.has_fee()

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"


# =========================================================
# VENDOR REGISTRATION
# =========================================================
class VendorRegistration(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="vendor_registrations"
    )

    data = models.JSONField(blank=True, null=True)

    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} → {self.event.title} (Vendor)"