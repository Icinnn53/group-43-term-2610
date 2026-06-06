from django import forms
from .models import Owner, Stall


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['name', 'phone', 'social_media', 'description']


class StallForm(forms.ModelForm):

    class Meta:
        model = Stall
        fields = [
            'owner',
            'event',
            'name',
            'description',
            'location',
            'capacity',
            'rental_fee',
            'stall_image'
        ]

    # optional UX improvement (shows "-" nicely)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['event'].required = False
        self.fields['event'].empty_label = "- (No Event / Rental Stall)"