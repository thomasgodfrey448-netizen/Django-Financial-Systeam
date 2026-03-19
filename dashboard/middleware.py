from django.utils.deprecation import MiddlewareMixin

from .models import UserProfile


class EnsureUserProfileMiddleware(MiddlewareMixin):
    """Ensure every authenticated user has an associated UserProfile.

    This prevents template errors when referencing `user.profile` and ensures
    role-based checks work consistently (e.g., superusers are treated as admins).
    """

    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            # Create profile for users who do not have one yet.
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'admin' if user.is_superuser else 'user'}
            )
        return None
