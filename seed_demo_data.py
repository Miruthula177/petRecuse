import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petrescue_core.settings')
django.setup()

from django.contrib.auth.models import User
from petrescue_app.models import PetReport, Notification, AdoptablePet, AdoptionRequest
import datetime

def seed():
    # 1. Create Admin User
    admin_user, created = User.objects.get_or_create(username='admin')
    if created or not admin_user.check_password('admin123'):
        admin_user.set_password('admin123')
        admin_user.first_name = 'Portal'
        admin_user.last_name = 'Administrator'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.email = 'admin@petrescue.org'
        admin_user.save()
        print("Created Superuser: admin / admin123")

    # 2. Create Normal User
    normal_user, created = User.objects.get_or_create(username='john_doe')
    if created or not normal_user.check_password('password123'):
        normal_user.set_password('password123')
        normal_user.first_name = 'John'
        normal_user.last_name = 'Doe'
        normal_user.email = 'john@example.com'
        normal_user.save()
        print("Created Normal User: john_doe / password123")

    # 3. Create Sample Pet Reports
    reports_data = [
        {
            'user': normal_user,
            'report_type': 'LOST',
            'pet_type': 'Dog',
            'pet_name': 'Max',
            'breed': 'Golden Retriever',
            'color': 'Golden / Blonde',
            'location': 'Central Park, MG Road',
            'lost_found_date': datetime.date(2025, 9, 18),
            'description': 'Friendly golden retriever wearing a blue leather collar with silver tags.',
            'image': 'pet_photos/sample_dog.jpg',
            'contact_phone': '+91 9876543210',
            'contact_email': 'john@example.com',
            'status': 'APPROVED',
            'admin_notes': 'Verified through owner phone verification.'
        },
        {
            'user': normal_user,
            'report_type': 'FOUND',
            'pet_type': 'Cat',
            'pet_name': 'Luna',
            'breed': 'Persian',
            'color': 'White & Grey',
            'location': 'Sunset Boulevard, Block 4',
            'lost_found_date': datetime.date(2025, 9, 19),
            'description': 'Found near apartment complex lobby. Very affectionate, well groomed.',
            'image': 'pet_photos/sample_cat.jpg',
            'contact_phone': '+91 9876543210',
            'contact_email': 'john@example.com',
            'status': 'APPROVED',
            'admin_notes': 'Valid report confirmed.'
        },
        {
            'user': normal_user,
            'report_type': 'LOST',
            'pet_type': 'Dog',
            'pet_name': 'Rocky',
            'breed': 'German Shepherd',
            'color': 'Black & Tan',
            'location': 'Greenwood Avenue',
            'lost_found_date': datetime.date(2025, 9, 21),
            'description': 'Large German Shepherd, answers to Rocky. Wearing red harness.',
            'image': 'pet_photos/sample_dog.jpg',
            'contact_phone': '+91 9876543210',
            'contact_email': 'john@example.com',
            'status': 'PENDING',
            'admin_notes': ''
        }
    ]

    for data in reports_data:
        report, created_rep = PetReport.objects.get_or_create(
            user=data['user'],
            pet_name=data['pet_name'],
            defaults=data
        )
        if not created_rep and not report.image:
            report.image = data['image']
            report.save()

    # 4. Create Sample Adoptable Pets
    adoptable_data = [
        {
            'added_by': admin_user,
            'name': 'Bella',
            'species': 'Dog',
            'breed': 'Beagle',
            'age': 2,
            'gender': 'Female',
            'color': 'Tricolor',
            'location': 'Sunrise Rescue Shelter, City Center',
            'health_status': 'Fully Vaccinated, Neutered & Microchipped',
            'description': 'Bella is a gentle, playful 2-year-old Beagle who loves children, playing fetch, and outdoor walks.',
            'image': 'pet_photos/sample_dog.jpg',
            'status': 'AVAILABLE'
        },
        {
            'added_by': admin_user,
            'name': 'Milo',
            'species': 'Cat',
            'breed': 'Tabby',
            'age': 1,
            'gender': 'Male',
            'color': 'Brown Striped',
            'location': 'Happy Tails Shelter, West End',
            'health_status': 'Vaccinated & De-wormed',
            'description': 'Milo is a calm, affectionate tabby cat who loves sunbathing on windowsills and cuddling.',
            'image': 'pet_photos/sample_cat.jpg',
            'status': 'AVAILABLE'
        }
    ]

    for data in adoptable_data:
        pet, created_pet = AdoptablePet.objects.get_or_create(
            name=data['name'],
            species=data['species'],
            defaults=data
        )
        if not created_pet and not pet.image:
            pet.image = data['image']
            pet.save()

    print("Demo Data Seeding Completed!")


if __name__ == '__main__':
    seed()
