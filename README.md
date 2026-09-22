# Pet Adoption and Rescue Management Portal (PetRescue)

[![Infosys Internship Project](https://img.shields.io/badge/Infosys_Internship-Project-blue.svg)](https://www.infosys.com/)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Django 6.1](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![MySQL Ready](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-orange.svg)](https://www.mysql.com/)

A full-stack, verified digital platform for managing lost pets, found pets, pet rescue activities, and **Pet Adoption**. Developed as an **Infosys Internship Project**.

---

## 🔑 Key Modules & Features

### A. Pet Rescue Module
- **Lost & Found Pet Reports**: Submit lost pet or found pet reports with species, breed, color, location, date, contact details, and pet image upload.
- **Admin Rescue Verification**: Staff review incoming reports before publishing them to the public search registry.
- **Search Approved Pets**: Filter verified rescue reports by species, breed, color, and location.

### B. Pet Adoption Module (New)
- **Adoptable Pet Listings (`/adoption/`)**: Public search registry for adoptable pets filtered by species, breed, age, and location.
- **Adoption Pet Details (`/adoption/<id>/`)**: Full profile detailing pet health status, age, gender, location, personality traits, and photo.
- **Adoption Request Submission (`/adoption/<id>/request/`)**: Logged-in users submit adoption applications detailing housing setup, pet experience, reason for adoption, and contact hours.
- **My Adoption Requests (`/my-adoption-requests/`)**: User portal page tracking application status (`PENDING` [Yellow], `APPROVED` [Green], `REJECTED` [Red]).
- **Admin Adoption Management (`/admin-portal/adoption/`)**: Admin portal to list new adoptable pets (`/admin-portal/adoption/add/`), review applications (`/admin-portal/adoption-request/<id>/`), approve/reject applications, attach reviewer feedback notes, and update pet availability.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.14 + Django 6.1
- **Database Engine**: MySQL (via PyMySQL connector `django.db.backends.mysql`) with automatic SQLite3 development fallback.
- **Frontend**: HTML5, Vanilla JavaScript, Custom Glassmorphic CSS Styling.
- **Authentication**: Built-in Django Authentication & Permission System (`@login_required`, `@staff_member_required`).
- **File Storage**: Django Media Storage (`media/pet_photos/` and `media/adoption_photos/`).

---

## 📁 Project Structure

```
Pet Adoption and Rescue Management Porta/
├── manage.py                   # Django CLI management script
├── seed_demo_data.py           # Database demo seeding script
├── MYSQL_SETUP.md              # Complete MySQL setup guide
├── DFD_DOCUMENTATION.md        # Updated DFD Level 0 & Level 1 documentation
├── README.md                   # Project overview & instructions
├── petrescue_core/             # Core project configuration
│   ├── __init__.py             # PyMySQL driver bridge setup
│   ├── settings.py             # Environment variables & database config
│   ├── urls.py                 # Main URL router
├── petrescue_app/              # Application module
│   ├── models.py               # PetReport, Notification, AdoptablePet, AdoptionRequest
│   ├── views.py                # 17 view controllers & auth logic
│   ├── forms.py                # Forms for Rescue, User Auth, AdoptablePet, AdoptionRequest
│   ├── admin.py                # Django admin site registrations
│   ├── urls.py                 # App URL patterns (Rescue + Adoption)
│   ├── signals.py              # Automated notification signals for Rescue & Adoption
│   └── tests.py                # Automated test suite (12 test cases)
├── templates/                  # 17 HTML Templates
│   ├── base.html               # Master layout & navbar (Rescue + Adoption links)
│   ├── home.html               # Landing page with hero, counters, & adoptable pets preview
│   ├── adoption_listings.html  # Adoptable pets search registry
│   ├── adoption_detail.html    # Adoptable pet detail view
│   ├── adoption_request.html   # Adoption application form
│   ├── my_adoption_requests.html # User's adoption applications table
│   ├── admin_adoption.html     # Admin adoption management dashboard
│   ├── admin_add_adoptable_pet.html # Admin form to list adoptable pet
│   └── admin_review_adoption.html # Admin adoption request decision view
```

---

## 🚀 Getting Started & Local Setup

```bash
# Navigate to project directory
cd "Pet Adoption and Rescue Management Porta"

# Activate virtual environment
.\.venv\Scripts\activate

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Seed initial portal users, rescue reports, and adoptable pets
python seed_demo_data.py

# Start development server
python manage.py runserver 8000
```

Open browser at: **`http://127.0.0.1:8000`**

---

## 🔑 Default Portal Credentials

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Rescue & Adoption Admin Portals |
| **Normal User** | `john_doe` | `password123` | Rescue Reports & Adoption Applications |

---

## 🧪 Running Automated Tests

To run the complete 12-test automated suite covering Rescue & Adoption modules:

```bash
python manage.py test
```

Expected Output:
```
Ran 12 tests in 87.650s
OK
```
