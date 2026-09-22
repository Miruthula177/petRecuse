from django.contrib import admin
from .models import PetReport, Notification, AdoptablePet, AdoptionRequest

@admin.register(PetReport)
class PetReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type', 'pet_type', 'pet_name', 'breed', 'color', 'location', 'status', 'created_at')
    list_filter = ('status', 'report_type', 'pet_type', 'created_at')
    search_fields = ('pet_name', 'breed', 'color', 'location', 'description', 'contact_phone', 'contact_email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)


@admin.register(AdoptablePet)
class AdoptablePetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'species', 'breed', 'age', 'gender', 'location', 'status', 'created_at')
    list_filter = ('status', 'species', 'gender', 'created_at')
    search_fields = ('name', 'breed', 'location', 'description', 'health_status')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'adoptable_pet', 'housing_type', 'status', 'created_at')
    list_filter = ('status', 'housing_type', 'created_at')
    search_fields = ('user__username', 'adoptable_pet__name', 'contact', 'reason')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


