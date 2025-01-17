from .models import PendingChange

def pending_changes(request):
    """
    Context processor to add PendingChanges to the template context for admins.
    """
    if request.user.is_authenticated and request.user.is_staff:  # Verifica si el usuario es admin
        pending_changes = PendingChange.objects.filter(approved__isnull=True)
        number_of_pending_changes = pending_changes.count()
        return {
            'pending_changes': pending_changes,
            'number_of_pending_changes': number_of_pending_changes,
                }
    return {'pending_changes': [], 'number_of_pending_changes': 0}
