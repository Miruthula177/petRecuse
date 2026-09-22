from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from petrescue_app.models import PetReport, Notification, AdoptablePet, AdoptionRequest
import datetime

class PetRescueTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create normal user
        self.user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe'
        )

        # Create secondary user
        self.other_user = User.objects.create_user(
            username='janedoe',
            email='jane@example.com',
            password='Password123!',
            first_name='Jane',
            last_name='Doe'
        )
        
        # Create admin user
        self.admin = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User'
        )

    # ==========================================================================
    # RESCUE MODULE TESTS
    # ==========================================================================

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'brandnewuser',
            'full_name': 'Jane Smith',
            'email': 'janesmith@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='brandnewuser').exists())


    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'johndoe',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_pet_report_creation(self):
        self.client.login(username='johndoe', password='Password123!')
        response = self.client.post(reverse('report_lost'), {
            'pet_type': 'Dog',
            'pet_name': 'Buddy',
            'breed': 'Golden Retriever',
            'color': 'Golden',
            'location': 'Downtown Park',
            'lost_found_date': '2026-09-20',
            'description': 'Friendly golden retriever with a blue collar.',
            'contact_phone': '9876543210',
            'contact_email': 'john@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PetReport.objects.filter(pet_name='Buddy').exists())

    def test_default_pending_status(self):
        report = PetReport.objects.create(
            user=self.user,
            report_type='LOST',
            pet_type='Dog',
            pet_name='Max',
            breed='Beagle',
            color='Tri-color',
            location='Main Street',
            lost_found_date=datetime.date(2026, 9, 21),
            description='Lost beagle.',
            contact_phone='9876543210',
            contact_email='john@example.com'
        )
        self.assertEqual(report.status, 'PENDING')

    def test_admin_approval(self):
        report = PetReport.objects.create(
            user=self.user,
            report_type='LOST',
            pet_type='Cat',
            pet_name='Whiskers',
            breed='Persian',
            color='White',
            location='Central Park',
            lost_found_date=datetime.date(2026, 9, 21),
            description='White fluffy cat.',
            contact_phone='9876543210',
            contact_email='john@example.com'
        )
        self.client.login(username='adminuser', password='AdminPassword123!')
        response = self.client.post(reverse('admin_verify', args=[report.id]), {
            'action': 'approve',
            'admin_notes': 'Verified valid report.',
        })
        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, 'APPROVED')

    # ==========================================================================
    # ADOPTION MODULE TESTS (Section 9 Specs)
    # ==========================================================================

    def test_create_adoptable_pet_and_listings(self):
        pet = AdoptablePet.objects.create(
            added_by=self.admin,
            name='Bella',
            species='Dog',
            breed='Beagle',
            age=2,
            gender='Female',
            color='Tricolor',
            location='City Shelter',
            description='Playful beagle.',
            status='AVAILABLE'
        )
        self.assertEqual(pet.status, 'AVAILABLE')

        # Public listing response check
        response = self.client.get(reverse('adoption_listings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bella')

    def test_adoptable_pet_filters_and_unavailable_exclusion(self):
        available_dog = AdoptablePet.objects.create(
            added_by=self.admin,
            name='Rex',
            species='Dog',
            breed='German Shepherd',
            age=3,
            gender='Male',
            location='North Shelter',
            description='Strong Shepherd.',
            status='AVAILABLE'
        )
        adopted_dog = AdoptablePet.objects.create(
            added_by=self.admin,
            name='Cooper',
            species='Dog',
            breed='Poodle',
            age=1,
            gender='Male',
            location='South Shelter',
            description='Friendly poodle.',
            status='ADOPTED'
        )

        # Test species filter
        response = self.client.get(reverse('adoption_listings'), {'species': 'Dog', 'breed': 'German'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rex')
        self.assertNotContains(response, 'Cooper')  # Adopted pet excluded

    def test_adoption_request_submission_authenticated_vs_anonymous(self):
        pet = AdoptablePet.objects.create(
            added_by=self.admin,
            name='Milo',
            species='Cat',
            breed='Tabby',
            age=1,
            gender='Male',
            location='West Shelter',
            description='Cute tabby.',
            status='AVAILABLE'
        )

        # Anonymous request attempt should redirect to login
        anon_response = self.client.get(reverse('adoption_request', args=[pet.id]))
        self.assertEqual(anon_response.status_code, 302)

        # Logged-in user request submission
        self.client.login(username='johndoe', password='Password123!')
        response = self.client.post(reverse('adoption_request', args=[pet.id]), {
            'housing_type': 'Own House',
            'experience': 'Had 2 cats previously.',
            'reason': 'Looking for a loving indoor cat.',
            'contact': '+91 9876543210',
        })
        self.assertEqual(response.status_code, 302)
        
        req = AdoptionRequest.objects.get(user=self.user, adoptable_pet=pet)
        self.assertEqual(req.status, 'PENDING')
        self.assertEqual(req.user, self.user)
        self.assertEqual(req.adoptable_pet, pet)

    def test_user_views_only_own_adoption_requests(self):
        pet = AdoptablePet.objects.create(
            added_by=self.admin,
            name='Daisy',
            species='Dog',
            breed='Pug',
            age=2,
            gender='Female',
            location='East Shelter',
            description='Pug dog.',
            status='AVAILABLE'
        )
        req_john = AdoptionRequest.objects.create(
            user=self.user,
            adoptable_pet=pet,
            housing_type='Own House',
            experience='Pug lover',
            reason='Family pet',
            contact='9876543210',
            status='PENDING'
        )

        # Log in as Jane
        self.client.login(username='janedoe', password='Password123!')
        response = self.client.get(reverse('my_adoption_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '#APP-' + str(req_john.id))

    def test_staff_approve_adoption_request_and_notification(self):
        pet = AdoptablePet.objects.create(
            added_by=self.admin,
            name='Luna',
            species='Cat',
            breed='Siamese',
            age=1,
            gender='Female',
            location='Central Shelter',
            description='Siamese cat.',
            status='AVAILABLE'
        )
        req = AdoptionRequest.objects.create(
            user=self.user,
            adoptable_pet=pet,
            housing_type='Rented Apartment',
            experience='Good experience',
            reason='Adopt indoor cat',
            contact='9876543210',
            status='PENDING'
        )

        # Log in as staff
        self.client.login(username='adminuser', password='AdminPassword123!')
        response = self.client.post(reverse('admin_review_adoption_request', args=[req.id]), {
            'action': 'approve',
            'admin_notes': 'Application verified and approved.',
        })
        self.assertEqual(response.status_code, 302)
        req.refresh_from_db()
        pet.refresh_from_db()

        self.assertEqual(req.status, 'APPROVED')
        self.assertEqual(pet.status, 'ADOPTED')

        # Check notification created for user
        self.assertTrue(Notification.objects.filter(user=self.user, title__icontains='Approved').exists())

    def test_staff_reject_adoption_request_and_notification(self):
        pet = AdoptablePet.objects.create(
            added_by=self.admin,
            name='Charlie',
            species='Dog',
            breed='Labrador',
            age=3,
            gender='Male',
            location='Downtown Shelter',
            description='Labrador dog.',
            status='AVAILABLE'
        )
        req = AdoptionRequest.objects.create(
            user=self.user,
            adoptable_pet=pet,
            housing_type='Other',
            experience='None',
            reason='Fun pet',
            contact='9876543210',
            status='PENDING'
        )

        self.client.login(username='adminuser', password='AdminPassword123!')
        response = self.client.post(reverse('admin_review_adoption_request', args=[req.id]), {
            'action': 'reject',
            'admin_notes': 'Housing conditions not suitable.',
        })
        self.assertEqual(response.status_code, 302)
        req.refresh_from_db()

        self.assertEqual(req.status, 'REJECTED')
        self.assertTrue(Notification.objects.filter(user=self.user, title__icontains='Status Update').exists())

    def test_unauthorized_user_cannot_access_admin_adoption(self):
        self.client.login(username='johndoe', password='Password123!')
        response = self.client.get(reverse('admin_adoption'))
        self.assertEqual(response.status_code, 302)
