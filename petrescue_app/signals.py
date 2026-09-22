from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import PetReport, Notification, AdoptionRequest

@receiver(pre_save, sender=PetReport)
def track_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = PetReport.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except PetReport.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=PetReport)
def notify_status_change(sender, instance, created, **kwargs):
    old_status = getattr(instance, '_old_status', None)
    
    # Notify if status changed from previous value
    if not created and old_status and old_status != instance.status:
        if instance.status == 'APPROVED':
            title = f"Report Approved: {instance.pet_type} ({instance.get_report_type_display()})"
            msg = f"Your report for a {instance.pet_type} at {instance.location} has been APPROVED by the administrator and is now publicly searchable."
            if instance.admin_notes:
                msg += f"\nAdmin Notes: {instance.admin_notes}"
            Notification.objects.create(user=instance.user, report=instance, title=title, message=msg)
            
            # Check for matching reports (e.g. if this is LOST, check APPROVED FOUND with same pet_type)
            opposite_type = 'FOUND' if instance.report_type == 'LOST' else 'LOST'
            matching_reports = PetReport.objects.filter(
                status='APPROVED',
                report_type=opposite_type,
                pet_type=instance.pet_type
            ).exclude(pk=instance.pk)
            
            for match in matching_reports:
                # Notify current user of potential match
                match_title = f"Potential Match Found: {match.pet_type}"
                match_msg = f"A matching {match.get_report_type_display()} report ({match.breed}, {match.color}) at '{match.location}' is available on PetRescue!"
                Notification.objects.create(user=instance.user, report=match, title=match_title, message=match_msg)
                
        elif instance.status == 'REJECTED':
            title = f"Report Rejected: {instance.pet_type} ({instance.get_report_type_display()})"
            msg = f"Your report for a {instance.pet_type} at {instance.location} was REJECTED by the administrator."
            if instance.admin_notes:
                msg += f"\nReason: {instance.admin_notes}"
            Notification.objects.create(user=instance.user, report=instance, title=title, message=msg)


@receiver(pre_save, sender=AdoptionRequest)
def track_previous_adoption_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = AdoptionRequest.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except AdoptionRequest.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=AdoptionRequest)
def notify_adoption_status_change(sender, instance, created, **kwargs):
    old_status = getattr(instance, '_old_status', None)

    if not created and old_status and old_status != instance.status:
        if instance.status == 'APPROVED':
            title = f"Adoption Application Approved! 🎉"
            msg = f"Congratulations! Your adoption request for '{instance.pet.name}' ({instance.pet.breed}) has been APPROVED by the portal administrator."
            if instance.admin_notes:
                msg += f"\nAdmin Notes: {instance.admin_notes}"
            Notification.objects.create(user=instance.applicant, title=title, message=msg)
            
            # Update pet status to ADOPTED
            instance.pet.status = 'ADOPTED'
            instance.pet.save()

        elif instance.status == 'REJECTED':
            title = f"Adoption Application Status Update"
            msg = f"Your adoption request for '{instance.pet.name}' was not approved at this time."
            if instance.admin_notes:
                msg += f"\nReason: {instance.admin_notes}"
            Notification.objects.create(user=instance.applicant, title=title, message=msg)

