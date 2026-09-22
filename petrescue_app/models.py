from django.db import models
from django.contrib.auth.models import User

class PetReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('LOST', 'Lost Pet'),
        ('FOUND', 'Found Pet'),
    ]

    PET_TYPE_CHOICES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pet_reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES, db_index=True)
    pet_type = models.CharField(max_length=20, choices=PET_TYPE_CHOICES, db_index=True)
    pet_name = models.CharField(max_length=100, blank=True, null=True, help_text="Optional for found pets")
    breed = models.CharField(max_length=100, db_index=True)
    color = models.CharField(max_length=50, db_index=True)
    location = models.CharField(max_length=255, db_index=True)
    lost_found_date = models.DateField(help_text="Date pet was lost or found")
    description = models.TextField()
    image = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Notes/reason provided by admin upon verification")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        name_str = f" ({self.pet_name})" if self.pet_name else ""
        return f"[{self.get_report_type_display()}] {self.pet_type}{name_str} - {self.location} ({self.status})"

    @property
    def badge_class(self):
        if self.status == 'APPROVED':
            return 'badge-approved'
        elif self.status == 'REJECTED':
            return 'badge-rejected'
        return 'badge-pending'

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            try:
                return self.image.url
            except ValueError:
                pass
        if self.pet_type == 'Cat':
            return '/static/images/default_cat.jpg'
        return '/static/images/default_dog.jpg'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    report = models.ForeignKey(PetReport, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class AdoptablePet(models.Model):
    SPECIES_CHOICES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available for Adoption'),
        ('PENDING_ADOPTION', 'Pending Adoption Review'),
        ('ADOPTED', 'Adopted'),
        ('INACTIVE', 'Inactive / Withdrawn'),
    ]

    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoptable_pets_added')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES, db_index=True)
    breed = models.CharField(max_length=100, db_index=True)
    age = models.PositiveIntegerField(help_text="Age in years or months")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    color = models.CharField(max_length=50, blank=True, default='')
    location = models.CharField(max_length=255, db_index=True)
    health_status = models.CharField(max_length=255, default='Vaccinated, De-wormed & Healthy')
    description = models.TextField()
    image = models.ImageField(upload_to='adoption_photos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.species} - {self.breed}) - [{self.status}]"

    @property
    def pet_type(self):
        return self.species

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            try:
                return self.image.url
            except ValueError:
                pass
        if self.species == 'Cat':
            return '/static/images/default_cat.jpg'
        return '/static/images/default_dog.jpg'

    @property
    def badge_class(self):
        if self.status == 'AVAILABLE':
            return 'badge-approved'
        elif self.status in ('ADOPTED', 'INACTIVE'):
            return 'badge-rejected'
        return 'badge-pending'


class AdoptionRequest(models.Model):
    HOUSING_CHOICES = [
        ('Own House', 'Own House'),
        ('Rented Apartment', 'Rented Apartment'),
        ('Farm / Villa', 'Farm / Villa'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_requests')
    adoptable_pet = models.ForeignKey(AdoptablePet, on_delete=models.CASCADE, related_name='adoption_requests')
    housing_type = models.CharField(max_length=50, choices=HOUSING_CHOICES, default='Own House')
    experience = models.TextField(help_text="Previous pet experience")
    reason = models.TextField(help_text="Reason for adoption")
    contact = models.CharField(max_length=100, help_text="Contact phone number or preferred contact method")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Reviewer notes from adoption portal admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Adoption Request by {self.user.username} for {self.adoptable_pet.name} ({self.status})"

    @property
    def applicant(self):
        return self.user

    @property
    def pet(self):
        return self.adoptable_pet

    @property
    def badge_class(self):
        if self.status == 'APPROVED':
            return 'badge-approved'
        elif self.status == 'REJECTED':
            return 'badge-rejected'
        return 'badge-pending'
