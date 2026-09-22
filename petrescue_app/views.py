from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from .models import PetReport, Notification, AdoptablePet, AdoptionRequest
from .forms import UserRegistrationForm, PetReportForm, AdminVerificationForm, AdoptablePetForm, AdoptionRequestForm, AdminAdoptionReviewForm


def staff_required(login_url='login'):
    return user_passes_test(lambda u: u.is_active and u.is_staff, login_url=login_url)


def home_view(request):
    total_lost = PetReport.objects.filter(report_type='LOST', status='APPROVED').count()
    total_found = PetReport.objects.filter(report_type='FOUND', status='APPROVED').count()
    reunited_count = PetReport.objects.filter(status='APPROVED').count() // 2
    
    recent_reports = PetReport.objects.filter(status='APPROVED')[:6]
    adoptable_pets = AdoptablePet.objects.filter(status='AVAILABLE')[:4]
    
    context = {
        'total_lost': total_lost,
        'total_found': total_found,
        'reunited_count': reunited_count,
        'recent_reports': recent_reports,
        'adoptable_pets': adoptable_pets,
    }
    return render(request, 'home.html', context)



def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to PetRescue, {user.first_name or user.username}! Your account was created successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    user_reports = PetReport.objects.filter(user=request.user)
    pending_count = user_reports.filter(status='PENDING').count()
    approved_count = user_reports.filter(status='APPROVED').count()
    rejected_count = user_reports.filter(status='REJECTED').count()
    
    notifications = Notification.objects.filter(user=request.user)[:5]
    recent_reports = user_reports[:5]
    
    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'notifications': notifications,
        'recent_reports': recent_reports,
    }
    return render(request, 'dashboard.html', context)


@login_required
def report_lost_view(request):
    if request.method == 'POST':
        form = PetReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.report_type = 'LOST'
            report.status = 'PENDING'
            report.save()
            messages.success(request, "Your Lost Pet report has been submitted successfully! It is now pending administrator verification.")
            return redirect('my_reports')
        else:
            messages.error(request, "Please fix the errors in your report submission.")
    else:
        form = PetReportForm(initial={'contact_email': request.user.email})

    return render(request, 'report_lost.html', {'form': form})


@login_required
def report_found_view(request):
    if request.method == 'POST':
        form = PetReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.report_type = 'FOUND'
            report.status = 'PENDING'
            report.save()
            messages.success(request, "Your Found Pet report has been submitted successfully! It is now pending administrator verification.")
            return redirect('my_reports')
        else:
            messages.error(request, "Please fix the errors in your report submission.")
    else:
        form = PetReportForm(initial={'contact_email': request.user.email})

    return render(request, 'report_found.html', {'form': form})


def search_view(request):
    # Only search approved reports
    reports = PetReport.objects.filter(status='APPROVED')

    pet_type = request.GET.get('pet_type', '').strip()
    breed = request.GET.get('breed', '').strip()
    color = request.GET.get('color', '').strip()
    location = request.GET.get('location', '').strip()
    report_type = request.GET.get('report_type', '').strip()

    if pet_type:
        reports = reports.filter(pet_type__iexact=pet_type)
    if breed:
        reports = reports.filter(breed__icontains=breed)
    if color:
        reports = reports.filter(color__icontains=color)
    if location:
        reports = reports.filter(location__icontains=location)
    if report_type:
        reports = reports.filter(report_type=report_type)

    context = {
        'reports': reports,
        'filter_pet_type': pet_type,
        'filter_breed': breed,
        'filter_color': color,
        'filter_location': location,
        'filter_report_type': report_type,
        'total_results': reports.count(),
    }
    return render(request, 'search.html', context)


def report_detail_view(request, pk):
    report = get_object_or_404(PetReport, pk=pk)
    
    # Privacy check: If not APPROVED, only creator or staff can view
    if report.status != 'APPROVED':
        if not request.user.is_authenticated or (request.user != report.user and not request.user.is_staff):
            messages.error(request, "This pet report is currently pending verification or not available publicly.")
            return redirect('search')

    context = {
        'report': report,
        'is_owner_or_staff': request.user.is_authenticated and (request.user == report.user or request.user.is_staff),
    }
    return render(request, 'report_detail.html', context)


@login_required
def my_reports_view(request):
    reports = PetReport.objects.filter(user=request.user)
    return render(request, 'my_reports.html', {'reports': reports})


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    
    # Mark unread notifications as read
    unread = notifications.filter(is_read=False)
    if unread.exists():
        unread.update(is_read=True)
        
    return render(request, 'notifications.html', {'notifications': notifications})


@staff_required()
def admin_dashboard_view(request):
    total_reports = PetReport.objects.count()
    pending_reports = PetReport.objects.filter(status='PENDING')
    approved_count = PetReport.objects.filter(status='APPROVED').count()
    rejected_count = PetReport.objects.filter(status='REJECTED').count()
    total_users = User.objects.count()
    
    recent_activity = PetReport.objects.exclude(status='PENDING')[:10]

    context = {
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'pending_count': pending_reports.count(),
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_users': total_users,
        'recent_activity': recent_activity,
    }
    return render(request, 'admin_dashboard.html', context)


@staff_required()
def admin_verify_view(request, pk):
    report = get_object_or_404(PetReport, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '').strip()

        if action == 'approve':
            report.status = 'APPROVED'
            report.admin_notes = admin_notes
            report.save()
            messages.success(request, f"Report #{report.id} ({report.pet_type}) was APPROVED successfully.")
            return redirect('admin_dashboard')
        elif action == 'reject':
            report.status = 'REJECTED'
            report.admin_notes = admin_notes
            report.save()
            messages.warning(request, f"Report #{report.id} ({report.pet_type}) was REJECTED.")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid verification action.")

    context = {
        'report': report,
    }
    return render(request, 'admin_verify.html', context)


# ==============================================================================
# PET ADOPTION MODULE VIEWS
# ==============================================================================

def adoption_listings_view(request):
    pets = AdoptablePet.objects.filter(status='AVAILABLE')

    species = request.GET.get('species', '').strip()
    breed = request.GET.get('breed', '').strip()
    age = request.GET.get('age', '').strip()
    location = request.GET.get('location', '').strip()

    if species:
        pets = pets.filter(species__iexact=species)
    if breed:
        pets = pets.filter(breed__icontains=breed)
    if age:
        try:
            pets = pets.filter(age=int(age))
        except ValueError:
            pass
    if location:
        pets = pets.filter(location__icontains=location)

    context = {
        'pets': pets,
        'filter_species': species,
        'filter_breed': breed,
        'filter_age': age,
        'filter_location': location,
        'total_results': pets.count(),
    }
    return render(request, 'adoption_listings.html', context)


def adoption_detail_view(request, pk):
    pet = get_object_or_404(AdoptablePet, pk=pk)
    
    # Check if user already submitted a pending request
    has_pending_request = False
    if request.user.is_authenticated:
        has_pending_request = AdoptionRequest.objects.filter(
            user=request.user, 
            adoptable_pet=pet, 
            status='PENDING'
        ).exists()

    context = {
        'pet': pet,
        'has_pending_request': has_pending_request,
    }
    return render(request, 'adoption_detail.html', context)


@login_required
def adoption_request_view(request, pk):
    pet = get_object_or_404(AdoptablePet, pk=pk)

    if pet.status != 'AVAILABLE':
        messages.error(request, f"'{pet.name}' is currently not available for adoption.")
        return redirect('adoption_detail', pk=pet.pk)

    # Check for existing pending application
    if AdoptionRequest.objects.filter(user=request.user, adoptable_pet=pet, status='PENDING').exists():
        messages.info(request, f"You already have a pending adoption request submitted for '{pet.name}'.")
        return redirect('my_adoption_requests')

    if request.method == 'POST':
        form = AdoptionRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.adoptable_pet = pet
            req.status = 'PENDING'
            req.save()
            messages.success(request, f"Your adoption application for '{pet.name}' has been submitted successfully! Portal admins will review your request shortly.")
            return redirect('my_adoption_requests')
        else:
            messages.error(request, "Please fix the errors in your adoption application.")
    else:
        form = AdoptionRequestForm(initial={'contact': getattr(request.user, 'email', '')})

    context = {
        'pet': pet,
        'form': form,
    }
    return render(request, 'adoption_request.html', context)


@login_required
def my_adoption_requests_view(request):
    adoption_requests = AdoptionRequest.objects.filter(user=request.user)
    return render(request, 'my_adoption_requests.html', {'adoption_requests': adoption_requests})


@staff_required()
def admin_adoption_view(request):
    adoptable_pets = AdoptablePet.objects.all()
    adoption_requests = AdoptionRequest.objects.all()
    pending_requests = adoption_requests.filter(status='PENDING')

    context = {
        'adoptable_pets': adoptable_pets,
        'adoption_requests': adoption_requests,
        'pending_requests': pending_requests,
        'total_pets': adoptable_pets.count(),
        'available_count': adoptable_pets.filter(status='AVAILABLE').count(),
        'pending_req_count': pending_requests.count(),
    }
    return render(request, 'admin_adoption.html', context)


@staff_required()
def admin_add_adoptable_pet_view(request):
    if request.method == 'POST':
        form = AdoptablePetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.added_by = request.user
            pet.save()
            messages.success(request, f"Adoptable Pet '{pet.name}' was listed successfully!")
            return redirect('admin_adoption')
        else:
            messages.error(request, "Please fix the errors in the adoptable pet form.")
    else:
        form = AdoptablePetForm()

    return render(request, 'admin_add_adoptable_pet.html', {'form': form})


@staff_required()
def admin_review_adoption_request_view(request, pk):
    req = get_object_or_404(AdoptionRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '').strip()

        if action == 'approve':
            req.status = 'APPROVED'
            req.admin_notes = admin_notes
            req.save()
            messages.success(request, f"Adoption application by {req.user.username} for '{req.adoptable_pet.name}' was APPROVED!")
            return redirect('admin_adoption')
        elif action == 'reject':
            req.status = 'REJECTED'
            req.admin_notes = admin_notes
            req.save()
            messages.warning(request, f"Adoption application by {req.user.username} for '{req.adoptable_pet.name}' was REJECTED.")
            return redirect('admin_adoption')
        else:
            messages.error(request, "Invalid decision action.")

    context = {
        'req': req,
    }
    return render(request, 'admin_review_adoption.html', context)

