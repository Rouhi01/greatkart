from .models import ReviewRating
from django import forms


class ReviewRatingForms(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']