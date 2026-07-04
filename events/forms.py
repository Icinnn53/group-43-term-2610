from django import forms
from django.forms.widgets import DateInput, TimeInput
from datetime import datetime
from .models import Event


# =========================================================
# EVENT FORM
# =========================================================
class EventForm(forms.ModelForm):

    # -------------------------
    # Custom datetime split fields
    # -------------------------
    start_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    start_time = forms.TimeField(
        widget=TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    end_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    end_time = forms.TimeField(
        widget=TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    # -------------------------
    # Event options
    # -------------------------
    allow_vendors_collaborators = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    max_registrations = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave empty for unlimited'
        })
    )

    # -------------------------
    # Registration fee toggle
    # -------------------------
    enable_registration_fee = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'enableFee'
        })
    )

    registration_fee = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'feeAmount',
            'placeholder': 'Enter fee amount'
        })
    )

    # -------------------------
    # PAYMENT DETAILS
    # -------------------------
    bank_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maybank'
        })
    )

    bank_account_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John Tan'
        })
    )

    bank_account_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456789012'
        })
    )

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'location',
            'image',
            'allow_vendors_collaborators',
            'max_registrations',
            'enable_registration_fee',
            'registration_fee',
            'bank_name',
            'bank_account_name',
            'bank_account_number',
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    # =====================================================
    # VALIDATION
    # =====================================================
    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        start_time = cleaned_data.get("start_time")
        end_date = cleaned_data.get("end_date")
        end_time = cleaned_data.get("end_time")

        if all([start_date, start_time, end_date, end_time]):
            start = datetime.combine(start_date, start_time)
            end = datetime.combine(end_date, end_time)

            if end <= start:
                raise forms.ValidationError("End time must be after start time.")

        return cleaned_data

    # =====================================================
    # SAVE
    # =====================================================
    def save(self, commit=True):
        instance = super().save(commit=False)

        start_date = self.cleaned_data.get("start_date")
        start_time = self.cleaned_data.get("start_time")
        end_date = self.cleaned_data.get("end_date")
        end_time = self.cleaned_data.get("end_time")

        if all([start_date, start_time, end_date, end_time]):
            instance.start_date = datetime.combine(start_date, start_time)
            instance.end_date = datetime.combine(end_date, end_time)

        if not self.cleaned_data.get("enable_registration_fee"):
            instance.registration_fee = None
        else:
            instance.registration_fee = self.cleaned_data.get("registration_fee")

        instance.bank_name = self.cleaned_data.get("bank_name")
        instance.bank_account_name = self.cleaned_data.get("bank_account_name")
        instance.bank_account_number = self.cleaned_data.get("bank_account_number")

        if commit:
            instance.save()

        return instance


# =========================================================
# CONCERT REGISTRATION
# =========================================================
class ConcertRegistrationForm(forms.Form):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


# =========================================================
# TOURNAMENT REGISTRATION
# =========================================================
class TournamentRegistrationForm(forms.Form):
    team_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    full_name = forms.CharField(
        label="Team Leader Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    skill_level = forms.ChoiceField(
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('pro', 'Pro'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    team_size = forms.IntegerField(
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # -------------------------
    # 11 hardcoded team member fields
    # -------------------------
    team_member_1 = forms.CharField(
        label="Team Member 1",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_2 = forms.CharField(
        label="Team Member 2",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_3 = forms.CharField(
        label="Team Member 3",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_4 = forms.CharField(
        label="Team Member 4",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_5 = forms.CharField(
        label="Team Member 5",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_6 = forms.CharField(
        label="Team Member 6",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_7 = forms.CharField(
        label="Team Member 7",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_8 = forms.CharField(
        label="Team Member 8",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_9 = forms.CharField(
        label="Team Member 9",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_10 = forms.CharField(
        label="Team Member 10",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    team_member_11 = forms.CharField(
        label="Team Member 11",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    additional_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


# =========================================================
# BAZAAR REGISTRATION
# =========================================================
class BazaarRegistrationForm(forms.Form):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    contact_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    stall_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    item_selling = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    social_media = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


# =========================================================
# VENDOR REGISTRATION
# =========================================================
class VendorRegistrationForm(forms.Form):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    contact_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    stall_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    item_selling = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    social_media = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


# =========================================================
# PAYMENT RECEIPT FORM
# =========================================================
class PaymentReceiptForm(forms.Form):
    payment_receipt = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    notes = forms.CharField(
        required=False,
        label='Notes (optional)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional notes for the organizer...'
        })
    )