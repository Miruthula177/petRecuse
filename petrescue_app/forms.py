from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import PetReport, AdoptablePet, AdoptionRequest


class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. John Doe'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'At least 8 characters'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter password'}),
        min_length=8
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique username'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name', '').strip()
        name_parts = full_name.split(' ', 1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class PetReportForm(forms.ModelForm):
    lost_found_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date Lost / Found"
    )

    class Meta:
        model = PetReport
        fields = [
            'pet_type', 'pet_name', 'breed', 'color', 'location', 
            'lost_found_date', 'description', 'image', 'contact_phone', 'contact_email'
        ]
        widgets = {
            'pet_type': forms.Select(attrs={'class': 'form-select'}),
            'pet_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pet name (optional for found pets)'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Labrador / Golden Retriever'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Golden / Black & White'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street, Area, City, State'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Distinctive features, collar, behavior, situation details...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@example.com'}),
        }


class AdminVerificationForm(forms.ModelForm):
    class Meta:
        model = PetReport
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for approval or rejection (visible to user)...'}),
        }


class AdoptablePetForm(forms.ModelForm):
    class Meta:
        model = AdoptablePet
        fields = [
            'name', 'species', 'breed', 'age', 'gender', 'color', 
            'location', 'health_status', 'description', 'image', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bella'}),
            'species': forms.Select(attrs={'class': 'form-select'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Beagle / Siamese'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age (e.g. 2)'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tricolor'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Shelter / City Location'}),
            'health_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Fully Vaccinated & Neutered'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Personality traits, habits, ideal family...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ['housing_type', 'experience', 'reason', 'contact']
        labels = {
            'housing_type': 'Housing Setup',
            'experience': 'Previous Pet Experience',
            'reason': 'Reason for Adoption',
            'contact': 'Contact Information (Phone & Preferred Hours)',
        }
        widgets = {
            'housing_type': forms.Select(attrs={'class': 'form-select'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your past experience with pets or current household pets...'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Why do you wish to adopt this pet? How will you care for them?'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210 (Available 9 AM - 6 PM)'}),
        }


class AdminAdoptionReviewForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Admin feedback / reason for decision...'}),
        }

