from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('report/lost/', views.report_lost_view, name='report_lost'),
    path('report/found/', views.report_found_view, name='report_found'),
    path('search/', views.search_view, name='search'),
    path('report/<int:pk>/', views.report_detail_view, name='report_detail'),
    path('my-reports/', views.my_reports_view, name='my_reports'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('admin-portal/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-portal/verify/<int:pk>/', views.admin_verify_view, name='admin_verify'),

    # Adoption Module Routes
    path('adoption/', views.adoption_listings_view, name='adoption_listings'),
    path('adoption/<int:pk>/', views.adoption_detail_view, name='adoption_detail'),
    path('adoption/<int:pk>/request/', views.adoption_request_view, name='adoption_request'),
    path('my-adoption-requests/', views.my_adoption_requests_view, name='my_adoption_requests'),
    path('admin-portal/adoption/', views.admin_adoption_view, name='admin_adoption'),
    path('admin-portal/adoption/add/', views.admin_add_adoptable_pet_view, name='admin_add_adoptable_pet'),
    path('admin-portal/adoption-request/<int:pk>/', views.admin_review_adoption_request_view, name='admin_review_adoption_request'),
]

